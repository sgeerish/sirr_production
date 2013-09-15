# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import time
from datetime import datetime
import math

import tools
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
from tools import config


class account_fixed_assets_method(osv.osv):

    def _close(self, cr, uid, id, asset_id, context={}):
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset = asset_obj.browse(cr, uid, asset_id)
        method = self.browse(cr, uid, id, context)
        if method.state <> 'close':
            self.write(cr, uid, id, {'state': 'close'})
        ok = (asset.state == 'normal')
        any_open = asset_obj.search(cr, uid, [('id','=',asset_id),('method_id','=',id),('state','<>','close')])
        if ok and not any_open:
            asset_obj.write(cr, uid, asset.id, {'state': 'close'}, context)
        return True

    def _initial(self, cr, uid, method, period_id, date, base, expense, acc_impairment, intervals_before, name, note, asset_id, context):
        asset_obj = self.pool.get('account.fixed.assets.asset')
        history_obj = self.pool.get('account.fixed.assets.history')
        period = self._check_date(cr, uid, period_id, date, context)
        asset = asset_obj.browse(cr, uid, asset_id)
        self._post_3lines_move(cr, uid, method=method, period = period, date = date, \
                    acc_third_id = acc_impairment, base = base, expense = expense, method_initial = True, context = context)
        self.validate(cr, uid, [method.id], context)
        if not asset.date:
            asset_obj.write(cr, uid, asset_id, {'date': date})
        if intervals_before:
            self.write(cr, uid, [method.id], {'intervals_before': intervals_before}, context)
        history_obj._history_line(cr, uid, "initial", method, name, \
                    base, expense, False, note, context)
        return True

    def _reval(self, cr, uid, method, period_id, date, base, expense, acc_impairment, name, note, context={}):
        period = self._check_date(cr, uid, period_id, date, context)
        direct = (method.account_asset_id.id == method.account_expense_id.id)
        expense = not direct and expense or False
        self._post_3lines_move(cr, uid, method = method, period = period, date = date, acc_third_id = acc_impairment, \
                    base = base, expense = expense, reval=True, context = context)
        self.pool.get('account.fixed.assets.history')._history_line(cr, uid, "reval", method, name, \
                    base, expense, False, note, context)
        return True

    def _abandon(self, cr, uid, methods, period_id, date, acc_abandon, name, note, asset_id, context={}):
        period = self._check_date(cr, uid, period_id, date, context)
        for method in methods:
            if method.state in ['open','suppressed','depreciated']:
                direct = (method.account_asset_id.id == method.account_expense_id.id)
                base = not direct and -method.value_total or - method.value_current 
                expense = not direct and -(method.value_total - method.value_current) or False
                if base:
                    self._post_3lines_move(cr, uid, method = method, period = period, date = date, acc_third_id = acc_abandon, \
                        base = base, expense = expense, context = context)
                self.pool.get('account.fixed.assets.history')._history_line(cr, uid, "abandon", method, name,
                    base, expense, False, note, context)
                self._close(cr, uid, method, asset_id, context)
        return True

    def _modif(self, cr, uid, method, method_duration, method_freq, method_progress_factor, value_residual, life, name, note, context={}):
        history_obj = self.pool.get('account.fixed.assets.history')
        data = {}
        note2 = _("Changing of method parameters to:") + \
                    _('\n   Number of Intervals: ') + str(method_duration) + \
                    _('\n   Intervals per Year: ') + str(method_freq) + \
                    _('\n   Progressive Factor: ') + str(method_progress_factor) + \
                    _('\n   Salvage Value: ') + str(value_residual or 0.0) + \
                    _('\n   Life Quantity: ') + str(life or 0.0) + \
                    "\n" + str(note or "")
        history_obj._history_line(cr, uid, "change", method, name, 0.0, 0.0, False, note2, context)
        data = {
            'method_duration': method_duration,
            'method_freq': method_freq,
            'method_progress_factor': method_progress_factor,
            'value_residual': value_residual,
            'life': life,
            }
        self.write(cr, uid, [method.id], data, context)
        return True

    def _suppress(self, cr, uid, methods, name, note, context={}):
        history_obj = self.pool.get('account.fixed.assets.history')
        for method in methods:
            if method.state == 'open':
                history_obj._history_line(cr, uid, "suppression", method, name, 0.0, 0.0, False, note, context)
                self.write(cr, uid, [method.id], {'state': 'suppressed'})
            else:
                raise osv.except_osv(_('Warning !'), _('Method is not Opened'))
        return True

    def _resume(self, cr, uid, methods, name, note, context={}):
        for method in methods:
            if method.state == 'suppressed':
                self.pool.get('account.fixed.assets.history')._history_line(cr, uid, "resuming", method, name, 0.0, 0.0, False, note, context )
                self.write(cr, uid, [method.id], {
                    'state': 'open'
                })
                method.state='open'
        return True

    def _get_next_period(self, cr, uid, context={}):
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(cr, uid, time.strftime('%Y-%m-%d'), context)
        if periods:
            cp = period_obj.browse(cr, uid, periods[0], context)
            return period_obj.next(cr, uid, cp, 1, context)
        else:
            return False

    _name = 'account.fixed.assets.method'
    _description = 'Fixed Assets Depreciation Methods'

    _columns = {
        'name': fields.char('Method name', size=64, select=1, required=True, readonly=True, states={'draft':[('readonly',False)]}),

        'method': fields.selection([('linear','Straight-Line'),
                                    ('decbalance','Declining-Balance'),
                                    ('syd', 'Sum of Years Digits'),
                                    ('uop','Units of Production'),
                                    ('progressive','Progressive')],
                                   'Computation Method', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'method_progress_factor': fields.float('Progressive Factor', digits_compute=dp.get_precision('Account'),
                                               readonly=True, states={'draft':[('readonly',False)]},
                                               help = "Specify the factor of progression in depreciation. \
                                               Used in Declining-Balance and Progressive method only. \
                                               When linear depreciation is 20% per year, and you want apply \
                                               Double-Declining Balance you should choose Declining-Balance method and enter 0,40 (40%) as Progressive factor."),
        'method_duration': fields.integer('Number of Intervals', readonly=True,
                                          states={'draft':[('readonly',False)]},
                                          help = "How many intervals this asset is to be calculated in its life. \
                                          If asset was calculated in other system before specify Intervals Before too."),
        'method_freq': fields.integer('Intervals per Year', readonly=True,
                                      states={'draft':[('readonly',False)]},
                                      help = "Specify the number of depreciations to be made in year. \
                                      This number cannot be less then number of periods in year."),
        'life': fields.float('Life Quantity', readonly=True,
                             states={'draft':[('readonly',False)]},
                             help = "Quantity of production which make the asset method used up.\
                             Used only in Units of Production computation method and cannot be zero in this case."),
        'state': fields.selection([('draft','Draft'),
                                   ('open','Open'),
                                   ('suppressed','Suppressed'),
                                   ('depreciated','Depreciated'),
                                   ('close','Closed')], 'Method State',
                                  required = True,
                                  help = "Open - Ready for calculation.\nSuppressed - Not calculated.\nDepreciated - \
                                  Depreciation finished but method exists (can be sold or abandoned).\
                                  \nClosed - Asset method doesn't exist (sold or abandoned)."),

    }

    _defaults = {
        'state': lambda obj, cr, uid, context: 'draft',
        'method': lambda obj, cr, uid, context: 'linear',
        'method_progress_factor': lambda obj, cr, uid, context: 0.3,
        'method_duration': lambda obj, cr, uid, context: 5,
        'method_freq': lambda obj, cr, uid, context: 12,
    }

    def unlink(self, cr, uid, ids, context={}):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state != 'draft':
                raise osv.except_osv(_('Error !'), _('You can delete method only in Draft state !'))
        return super(account_fixed_assets_method, self).unlink(cr, uid, ids, context)

    def _check_method(self, cr, uid, ids):
        obj_self = self.browse(cr, uid, ids[0])
        if (12 % obj_self.method_freq) == 0:
            return True
        return False

    _constraints = [
        (_check_method,
         _('Error ! Number of intervals per year must be 1, 2, 3, 4, 6 or 12.'),
         ['method_freq']),
    ]

    def validate(self, cr, uid, ids, context={}):
        asset_obj = self.pool.get('account.fixed.assets.asset')
        methods = self.bowse(cr, uid, ids, context)
        for method in methods:
            self.write(cr, uid, ids, {'state':'open'}, context)
            asset_obj.write(cr, uid, [method.asset_id.id], {'state':'normal'}, context)
        return True

    def _post_3lines_move(self, cr, uid, method, period, date, acc_third_id, base=0.0, expense=0.0, method_initial=False, reval=False, context={}):
        '''
        Method is used to post Asset sale, revaluation, abandon and initial values (initial can create 4 lines move)
        '''
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        method_obj = self.pool.get('account.fixed.assets.method')
        move_data = {
            'journal_id': method.journal_id.id,
            'period_id': period.id,
            'date': date,
            'name': '/',
            'ref': method.name
            }
        move_id = move_obj.create(cr, uid, data)
        result = [move_id]
        entries =[]
        expense = expense and - expense or False 
        total = base
        if method_initial:
            residual = - total
        elif reval:
            residual = - (base + (expense or 0.0))  # expense is already negative
        else:
            residual =  method.value_current
        if expense:
            line_data = {
                'name': method.name or method.asset_id.name,
                'move_id': move_id,
                'account_id': method.account_expense_id.id,
                'debit': expense > 0 and expense or 0.0, 
                'credit': expense < 0 and -expense or 0.0,
                'ref': method.asset_id.code,
                'period_id': period.id,
                'journal_id': method.journal_id.id,
                'partner_id': method.asset_id.partner_id.id,
                'date': date,
                'asset_method_id': method.id      
                }
            id = move_line_obj.create(cr, uid, line_data)

            entries.append((4, id, False),)
            if method_initial:
                line1_data = {
                    'name': method.name or method.asset_id.name,
                    'move_id': move_id,
                    'account_id': method.account_actif_id.id,
                    'debit': expense > 0 and expense or 0.0,
                    'credit': expense < 0 and -expense or 0.0, 
                    'ref': method.asset_id.code,
                    'period_id': period.id,
                    'journal_id': method.journal_id.id,
                    'partner_id': method.asset_id.partner_id.id,
                    'date': date,
                    'asset_method_id': method.id      
                    }
                id_depr = move_line_obj.create(cr, uid, line1_data)
                entries.append((4, id_depr, False),)
                
        line2_data = {
            'name': method.name or method.asset_id.name,
            'move_id': move_id,
            'account_id': method.account_asset_id.id,
            'debit': total > 0 and total or 0.0, 
            'credit': total < 0 and -total or 0.0, 
            'ref': method.asset_id.code,
            'period_id': period.id,
            'journal_id': method.journal_id.id,
            'partner_id': method.asset_id.partner_id.id,
            'date': date,
            'asset_method_id': method.id     
            }
        id2 = move_line_obj.create(cr, uid, line2_data)
        
        line3_data = {
            'name': method.name or method.asset_id.name,
            'move_id': move_id,
            'account_id': acc_third_id,
            'debit': residual > 0 and residual or 0.0, 
            'credit': residual < 0 and -residual or 0.0, 
            'ref': method.asset_id.code,
            'period_id': period.id,
            'journal_id': method.journal_id.id,
            'partner_id': method.asset_id.partner_id.id,
            'date': date,
            'asset_method_id': method.id     
            }
        id3 = move_line_obj.create(cr, uid, line3_data)
        entries.append([(4, id2, False),(4, id3, False)])
        
        method_obj.write(cr, uid, [method.id], {'move_line_ids': entries})
        if method.journal_id.entry_posted:
            self.pool.get('account.move').post(cr, uid, move_id, context)
        return result

account_fixed_assets_method()

class account_fixed_assets_category(osv.osv):
    
    _name = 'account.fixed.assets.category'
    _description = 'Fixed Assets Category'
    
    _columns = {
        'code': fields.char('Asset Category Code', size=16, required=True, select=1),
        'name': fields.char('Asset Category', size=64, required=True, select=1),
        'note': fields.text('Note'),
        'account_asset_id': fields.many2one('account.account', 'Asset Account', required=True,
                                            help="Select account used for cost basis of asset.\
                                            It will be applied into invoice line when you select this asset in invoice line."),
        'account_depr_id': fields.many2one('account.account', 'Depreciation Account', required=True,
                                           help="Select account used for depreciation amount. \
                                           If you use direct method of depreciation this account should be the same as Asset Account."),
        'account_expense_id': fields.many2one('account.account', 'Depr. Expense Account', required=True,
                                              help="Select account used for depreciation expense (write-off)."),
        'method_id': fields.many2one('account.fixed.assets.method', 'Depreciation Method',
                                     help="Select the method used for depreciation"),
        'parent_id': fields.many2one('account.fixed.assets.category', 'Parent Category'),
        'child_ids': fields.one2many('account.fixed.assets.category', 'parent_id', 'Children Categories'),
        'state': fields.selection([('draft','Draft'), ('open','Open'), ('close','Closed')],
                                  'Category State',
                                  required=True,
                                  help="Open - Ready for calculation.\nClosed - Asset category cannot be used."),

    }
    
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            sql = "select distinct parent_id from account_fixed_assets_category where id in (%s)" % ','.join(map(str,ids))
            cr.execute(sql)
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True
    
    def validate(self, cr, uid, ids, context={}):
        categories = self.browse(cr, uid, ids, context)
        for category in categories:
            if category.state == 'draft':
                return self.write(cr, uid, [category.id], {'state':'open'}, context)


    _constraints = [
        (_check_recursion, _('Error ! You can not create recursive categories.'), ['parent_id'])
    ]

account_fixed_assets_category()


class account_fixed_assets_asset(osv.osv):

    _name = 'account.fixed.assets.asset'
    _description = 'Fixed Asset'

    def _amount_total(self, cr, uid, ids, name, args, context={}):
        if not ids:
            return {}
        res = {}
        for id in ids:
            res[id] = {}

            cr.execute("SELECT SUM(m.debit-m.credit) AS asset_value \
                            FROM account_fixed_assets_asset a \
                            LEFT JOIN account_move_line m \
                                ON (a.move_id=m.move_id) \
                            WHERE a.id = %s AND m.account_id = a.account_asset_id \
                            AND a.product_id=m.product_id" % (id, ))
            asset_value = cr.fetchone()[0] or 0.0
## TODO function to change value_current when account move approved

#            cr.execute("SELECT SUM(ml.debit-ml.credit) AS asset_depr \
#                            FROM account_fixed_assets_asset a \
#                            LEFT JOIN account_move_line ml \
#                                ON (a.id=ml.asset_id) \
#                            LEFT JOIN account_move m \
#                                ON (ml.move_id=m.id) \
#                            WHERE a.id = %s AND m.state = 'open' AND ml.account_id = a.account_depr_id" % (id, ))

            cr.execute("SELECT SUM(ml.debit-ml.credit) AS asset_depr \
                            FROM account_fixed_assets_asset a \
                            LEFT JOIN account_move_line ml \
                                ON (a.id=ml.asset_id) \
                            WHERE a.id = %s AND ml.account_id = a.account_depr_id" % (id, ))

            asset_depr = cr.fetchone()[0] or 0.0
            res[id]['value_total'] = asset_value
            res[id]['value_current'] = asset_value + asset_depr
        return res

#    def _amount_all(self, cr, uid, ids, name, args, context=None):
#        res = {}
#        for asset in self.browse(cr,uid, ids, context=context):
#            res[asset.id] = {
#                'amount_total': 0.0,
#                'amount_residual': 0.0,
#            }
#            for line in asset.move_line_ids:
#                res[asset.id]['amount_total'] += line.value_total
#                res[asset.id]['amount_residual'] += line.value_current
#        return res

    def _finish_depreciation(self, cr, uid, asset, context={}):
        if asset.state == 'open':
            self.pool.get('account.fixed.assets.asset').write(cr, uid, [asset.id], {
                'state': 'depreciated'
            })
            asset.state='depreciated'
        return True

#    def _get_method(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {}
#        result = {}
#        for method in self.pool.get('account.fixed.assets.method').browse(cr, uid, ids, context=context):
#            result[method.asset_id.id] = True
#        return result.keys()

    def _get_move_line(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        result = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            result[line.asset_id.id] = True
        return result.keys()

## TODO function to change value_current when account move approved
#    def _get_move(self, cr, uid, ids, context=None):
#        result = {}
#        raise osv.except_osv('Error !', self.pool.get('account.move').browse(cr, uid, ids, context=context).asset_id) 
#        for line in self.pool.get('account.move').browse(cr, uid, ids, context=context):
#            result[line.asset_id.id] = True
#        return result.keys()

    def clear(self, cr, uid, ids, context={}):
        method_obj = self.pool.get('account.fixed.assets.method')
        assets = self.browse(cr, uid, ids, context)
        for asset in assets:
            ok = True
            if asset.method_id and asset.method_id.state == 'draft':
                method_obj.unlink(cr, uid, [met.id], context)
            elif asset.method_id and asset.method_id.state != 'close':
                ok = False
            if ok:
                self.write(cr, uid, [asset.id], {'state':'close'}, context)
            else:
                raise osv.except_osv(_('Warning !'), _('This wizard works only when asset have just Draft and Closed methods !'))

        return True 

    _columns = {
        'name': fields.char('Asset', size=64, required=True, select=1),
        'code': fields.char('Asset Code', size=16, select=1, required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'tag': fields.char('Tag', size=32, required=False),
        'serial_no': fields.char('Asset S/N', size=32, required=False),
        'value_total': fields.float('Gross Value', digits_compute=dp.get_precision('Account'),
                                    readonly=True,
                                    states={'draft':[('readonly',False)]}, help="Initial gross value"),
        'value_current': fields.function(_amount_total, method=True,
                                         digits_compute=dp.get_precision('Account'),
                                         string='Current (book) Value', 
                                         store={
                                                'account.fixed.assets.asset': (lambda self, cr, uid, ids, c={}: ids, ['move_line_ids','state'], 10),
                                                'account.move.line': (_get_move_line, ['debit','credit','account_id','asset_id','product_id'], 10),
        ## TODO function to change value_current when account move approved
        #                'account.move': (_get_move, ['state', 'move_id', 'asset_id'], 10),                                                
                                                },
                                         multi='all'),

        'note': fields.text('Note'),
        'category_id': fields.many2one('account.fixed.assets.category', 'Asset Category', change_default=True),
        'location': fields.char('Location', size=32, readonly=True, states={'draft':[('readonly',False)]}, help = "Set this field before asset confirming. Later on you will have to use Change Location button."),
        'sequence': fields.integer('Seq.'),
        'date': fields.date('Date',readonly=True,
                            states={'draft':[('readonly',False)]},
                            help="Set this date or leave it empty to allow system set the first purchase date."),
        'state': fields.selection([('view','View'),('draft','Draft'),('open','Open'),('close','Closed'),('depreciated','Depreciated')],
                                  'Asset State', required=True,
                                  help="Open - Asset contains active methods (opened, suppressed or depreciated).\n \
                                  Closed - Asset doesn't exist. All methods are sold or abandoned."),
        'active': fields.boolean('Active'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null'),
        'currency_id': fields.many2one('res.currency', 'Currency', ondelete='set null'),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', required=True, readonly=True),
        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True,
                                   select=1, ondelete='set null',
                                   help="Link to the automatically generated Journal Items."),
        'account_asset_id': fields.many2one('account.account', 'Asset Account', required=True, readonly=True,
                                            states={'draft':[('readonly',False)]},
                                            help="Select account used for cost basis of asset. \
                                            It will be applied into invoice line when you select this asset in invoice line."),
        'account_depr_id': fields.many2one('account.account', 'Depreciation Account', required=True, readonly=True,
                                           states={'draft':[('readonly',False)]},
                                           help="Select account used for depreciation amounts. \
                                           If you use direct method of depreciation this account should be the same as Asset Account."),
        'account_expense_id': fields.many2one('account.account', 'Depr. Expense Account', required=True,
                                              readonly=True, states={'draft':[('readonly',False)]},
                                              help="Select account used for depreciation expense (write-off)."),
        'account_residual_id': fields.many2one('account.account', 'Sale Residual Account',
                                               help="Select account used for residual when asset is sold. You can change the account before sale operation."),
        'account_impairment_id': fields.many2one('account.account', 'Impairment Account',
                                                 help="Select account used for impairment amount. Used in revaluation."),
        'account_abandon_id': fields.many2one('account.account', 'Abandonment Account',
                                              help="Select account used for abandonment loss amount."),
        'journal_analytic_id': fields.many2one('account.analytic.journal', 'Analytic Journal', help="Not implemented yet."),
        'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', help="Not implemented yet."),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True,
                                     states={'draft':[('readonly',False)]}, help="Select period indicating first interval."),
#        'method_id': fields.many2one('account.fixed.assets.method', 'Depreciation Method', help = "Select the method used for depreciation"),
        'method_id': fields.related('method_id', type='many2one', relation='account.fixed.assets.method', string='Depreciation Method', store=True, help="Select the method used for depreciation"),
        'method_progress_factor': fields.float('Progressive Factor', digits_compute=dp.get_precision('Account'), readonly=True,
                                               states={'draft':[('readonly',False)]},
                                               help="Specify the factor of progression in depreciation. \
                                               Used in Declining-Balance and Progressive method only.\
                                               When linear depreciation is 20% per year, and you want apply \
                                               Double-Declining Balance you should choose Declining-Balance method and enter 0,40 (40%) as Progressive factor."),
        'method_duration': fields.integer('Depr. Duration (Years)', readonly=True, states={'draft':[('readonly',False)]},
                                          help="How many intervals this asset is to be calculated in its life.\
                                          If asset was calculated in other system before specify Intervals Before too."),
        'intervals_before' : fields.integer('Intervals Before', readonly=True, states={'draft':[('readonly',False)]},
                                            help="Number of intervals calculated before asset is managed in this system.\
                                            Used with Initial Values wizard. If you start asset in this system keep zero."),
        'method_freq': fields.integer('Frequency of writing', readonly=True, states={'draft':[('readonly',False)]},
                                      help="Specify the number of depreciations to be made in year."),
# TODO You can implement depreciation calculation from fixed date. 
#        'method_time': fields.selection([('interval','Interval'),('date','Start Date'),('endofyear','End of Year')], 'Time Method', readonly=True, states={'draft':[('readonly',False)]}, help="Not implemented yet."),
        'date_start' : fields.date('Start Date',readonly=True, states={'draft':[('readonly',False)]}, help="Date of depreciation calculation start."),
        'intervals_before' : fields.integer('Intervals Before', readonly=True, states={'draft':[('readonly',False)]},
                                            help="Number of intervals calculated before asset is managed in this system.\
                                            Used with Initial Values wizard. If you start asset in this system keep zero."),
        'value_residual': fields.float('Residual (salvage) Value', readonly=True, states={'draft':[('readonly',False)]},
                                       help="Value planned to be residual after full depreciation process"),
        'date_end': fields.date('Ending Date'),

        'history_ids': fields.one2many('account.fixed.assets.history', 'asset_id', 'History', readonly=True),
        'asset_track': fields.related('move_line_id','asset_track', relation='account.invoice.line', type='many2one', string='Track Asset', readonly=1),
        'asset_category_id': fields.related('move_line_id','asset_category_id', relation='account.invoice.line', type='many2one', string='Asset Category'),
        'move_line_ids': fields.one2many('account.move.line', 'asset_id', 'Move Line Entries', readonly=True, states={'draft':[('readonly',False)]}),
#        'usage_ids': fields.one2many('account.fixed.assets.method.usage', 'asset_method_id', 'Usage'),
    }
    
    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        journal_code = 'FAJ'
        journal_id = False
        if journal_code:
            ids = journal_obj.search(cr, uid, [('code', '=', journal_code)])
            if ids:
                journal_id = ids[0]
        return journal_id

#    def _default_journal(self, cr, uid, context=None):
#        if context.has_key('journal_id') and context['journal_id']:
#            journal = journal_obj.browse(cr, uid, context['journal_id'], context=context)
#            if journal.analytic_journal_id:
#                return journal.analytic_journal_id.id
#        return False

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'account.fixed.assets.code'),
        'active': lambda obj, cr, uid, context: True,
        'state': lambda obj, cr, uid, context: 'draft',
        'journal_id': _get_journal_id,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.fixed.assets.asset', context=c),
    }

    def unlink(self, cr, uid, ids, context={}):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state != 'draft':
                raise osv.except_osv(_('Error !'), _('You can delete assets only in Draft state !'))
        return super(account_fixed_assets_asset, self).unlink(cr, uid, ids, context)

    def _location(self, cr, uid, asset_id, location, name, note, context={}):
        asset = self.browse(cr, uid, asset_id, context)
        self.pool.get('account.fixed.assets.history').create(cr, uid, {
            'type': "transfer",
            'asset_id' : asset_id,
            'name': name,
#            'asset_total': asset.amount_total,
#            'asset_residual': asset.amount_residual,
            'note': _("Asset transfered to: ") + tools.ustr(location)+
                    "\n" + tools.ustr(note or ""),
        }, context)
        self.pool.get('account.fixed.assets.asset').write(cr, uid, [asset_id], {
            'location': location,
        }, context)
        return True

    def get_defaults(self, cr, uid, method_id, asset_category_id, context={}):
        method_obj = self.pool.get('account.fixed.assets.method')
        category_obj = self.pool.get('account.fixed.assets.category')
        if not asset_category_id:
            defaults_id = default_obj.search(cr,uid,[('method_type','=',method_id),('asset_category','=',False)])
        else:
            defaults_id = default_obj.search(cr,uid,[('method_type','=',method_id),('asset_category','=',asset_category_id)])
            if not defaults_id:
                asset_cat_obj = self.pool.get('account.fixed.assets.category')
                parent_cat_id = asset_category_id
                n = 100
                while asset_cat_obj.browse(cr, uid, parent_cat_id,{}).parent_id and not defaults_id and n != 0:
                    parent_cat_id = asset_cat_obj.browse(cr, uid, parent_cat_id,{}).parent_id.id
                    defaults_id = default_obj.search(cr,uid,[('method_type','=',method_id),('asset_category','=',parent_cat_id)])
                    n = n - 1
        return defaults_id and default_obj.browse(cr, uid, defaults_id[0],{}) or False

    def onchange_take_defaults(self, cr, uid, ids, method_id, name, asset_code, asset_name, asset_category_id, context={}):
        result = {}
        if method_id:
            defaults = self.get_defaults(cr, uid, method_id, asset_category_id, context)
            if defaults:
                result['account_expense_id'] = defaults.account_expense_id.id
                result['account_actif_id'] = defaults.account_actif_id.id
                result['account_asset_id'] = defaults.account_asset_id.id
                result['account_residual_id'] = defaults.account_residual_id.id
                result['journal_id'] =  defaults.journal_id.id
                result['journal_analytic_id'] = defaults.journal_analytic_id.id
                result['account_analytic_id'] =  defaults.account_analytic_id.id
                result['method'] = defaults.method
                result['method_progress_factor'] =  defaults.method_progress_factor
                result['method_duration'] = defaults.method_duration
                result['method_freq'] = defaults.method_freq
            as_code = asset_code or ""
            as_name = asset_name or ""
            type_code = self.pool.get('account.fixed.assets.method.type').browse(cr, uid, method_id,{}).code
            result['name'] = as_name + " (" + as_code + ")" + ' - ' + type_code 
        return {'value': result}
    
    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', \
                          type='out_invoice', partner_id=False, \
                          fposition_id=False, price_unit=False, \
                          address_invoice_id=False, currency_id=False, context=None):
        if context is None:
            context = {}
        company_id = context.get('company_id',False)
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined !'),_("You must first select a partner !") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {'categ_id': False}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0, 'categ_id': False}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        if type in ('out_invoice','out_refund'):
            a = res.product_tmpl_id.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.product_tmpl_id.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        result['name'] = res.partner_ref

        domain = {}
        result['uos_id'] = res.uom_id.id or uom or False
        if result['uos_id']:
            res2 = res.uom_id.category_id.id
            if res2:
                domain = {'uos_id':[('category_id','=',res2 )]}

        result['categ_id'] = res.categ_id.id
        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if uom:
            uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if res.uom_id.category_id.id == uom.category_id.id:
                new_price = res_final['value']['price_unit'] * uom.factor_inv
                res_final['value']['price_unit'] = new_price
        return res_final

    def validate(self, cr, uid, ids, context={}):
        assets = self.browse(cr, uid, ids, context)
        for asset in assets:
            if asset.state == 'draft':
                return self.write(cr, uid, [asset.id], {'state':'open'}, context)
            if asset.state == 'open':
                return self.write(cr, uid, [asset.id], {'state':'draft'}, context)


    def _compute_entries(self, cr, uid, asset, period, date, context={}):
        result = []
        if (asset.state=='open') and (period.date_start >= asset.period_id.date_start):
            usage = False
            period_ok = False
            last_move_line, compute_period = self._compute_last_calculated(cr, uid, asset, period, context)
            if compute_period:          # it was no calculation for period yet
                if asset.method_id.method == 'uop':
                    usage_obj = self.pool.get('account.fixed.assets.method.usage')
                    usage_ids = usage_obj.search(cr, uid, [('period_id','=',period.id),('asset_id','=',asset.id)])
                    usage = usage_ids and usage_obj.browse(cr, uid, usage_ids[0], context).usage or False
                else:
#      checks if the month corresponds with the frequency e.g. freq 4 meaning every 3 months, the month shall be 3,6,9,12
                    period_ok = ((datetime.strptime(period.date_stop, '%Y-%m-%d').month % (12 / asset.method_freq)) == 0)
                if (period_ok or usage):
                    result += self._compute_move(cr, uid, asset, period, date, usage, last_move_line, context)
        return result
    
#    def _compute_entries(self, cr, uid, asset, period_id, context={}):
#        result = []
#        date_start = self.pool.get('account.period').browse(cr, uid, period_id, context).date_start
#        for property in asset.property_ids:
#            if property.state=='open':
#                period = self._compute_period(cr, uid, property, context)
#                if period and (period.date_start<=date_start):
#                    result += self._compute_move(cr, uid, property, period, context)
#        return result

    def _compute_last_calculated(self, cr, uid, asset, period, context={}):
        cr.execute("SELECT m.id, m.period_id \
                        FROM account_move_line AS m \
                            WHERE m.asset_id = %s AND m.account_id = %s \
                            ORDER BY m.id DESC", (asset.id, asset.account_depr_id.id,))
        pid = cr.fetchone()
        if pid:
            periods_obj = self.pool.get('account.period')
            last_period = periods_obj.browse(cr, uid, pid[1], context)
            if last_period.date_start < period.date_start:
                ml_obj = self.pool.get('account.move.line')
                last_move_line = ml_obj.browse(cr, uid, pid[0], context)
                return last_move_line, True                # last move line exists and do compute
            else:
                return False, False        # last move line doesn't exists and don't compute
        return False, True            # last move line doesn't exists but do compute

    def _compute_move(self, cr, uid, asset, period, date, usage, last_move_line, context={}):
        result = []
        gross = asset.value_total - asset.value_residual
        to_writeoff = asset.value_current - asset.value_residual 

        if usage:                # Units of Production method
            amount = gross * usage / asset.life
        else:
            depr_entries_made = asset.intervals_before
            for line in asset.move_line_ids:
                if (line.account_id == asset.account_depr_id) and (line.period_id.date_start >= asset.period_id.date_start):
                    depr_entries_made += 1      # count depreciation already made
            intervals = asset.method_duration - depr_entries_made
            if intervals == 1:
                amount = to_writeoff
            else:
                if asset.method_id.method == 'linear':
                    amount = to_writeoff / intervals
                elif asset.method_id.method == 'progressive':    # probably obsolete method
                    amount = to_writeoff * asset.method_progress_factor
                elif asset.method_id.method == 'decbalance':
                    period_end = datetime.strptime(period.date_stop, '%Y-%m-%d')
                    if depr_entries_made == 0:
                        if asset.date_start:
                            period_start = datetime.strptime(asset.date_start, '%Y-%m-%d')
                        else:
                            period_start = datetime.strptime(asset.date, '%Y-%m-%d')
                        prorata = (12-period_start.month +1) / 12.00     # First year
                        amount = to_writeoff * prorata * asset.method_progress_factor / asset.method_freq 
                        #raise osv.except_osv('kAKA', amount)
                    elif (12 / period_end.month) == asset.method_freq:                      # First interval in calendar year
                        amount = to_writeoff * asset.method_progress_factor / asset.method_freq
                        if amount < (gross / asset.method_duration):   # In declining-balance when amount less than amount for linear it switches to linear
                            amount = gross / asset.method_duration
                    else:                                            # In other cases repeat last entry
                        amount = last_move_line.debit
                elif asset.method_id.method == 'syd':                         # Sum of Year Digits method
                    years = asset.method_duration / asset.method_freq
                    syd = years * (years + 1) / 2
                    year = years - math.floor(depr_entries_made / asset.method_freq)
                    if (depr_entries_made % asset.method_freq) == 0:                          # First interval in 12 month cycle
                        amount = gross * year / syd / asset.method_freq 
                    else:                                              # In other cases repeat last entry
                        amount = last_move_line.debit
        if amount > to_writeoff:
            amount = to_writeoff

        result = self._post_move(cr, uid, asset, period, date, amount, context)

        if (to_writeoff == amount): 
            self.pool.get('account.fixed.assets.asset')._finish_depreciation(cr, uid, asset, context)
        return result

    def _post_move(self, cr, uid, asset, period, date, amount, context={}):
        move_obj = self.pool.get('account.move')
        line_obj = self.pool.get('account.move.line')
        move_data = {
            'journal_id': asset.journal_id.id,
            'period_id': period.id,
            'date': date,
            'name': '/', 
            'ref': asset.name
            }
        move_id = move_obj.create(cr, uid, move_data)
        result = [move_id]
        line_data = {
            'name': asset.name,
            'move_id': move_id,
            'account_id': asset.account_expense_id.id,
            'debit': amount>0 and amount or 0.0,  
            'credit': amount<0 and -amount or 0.0, 
            'ref': asset.code,
            'period_id': period.id,
            'journal_id': asset.journal_id.id,
            'partner_id': asset.partner_id.id,
            'date': date,
            'asset_id': asset.id      
            }
        id1 = line_obj.create(cr, uid, line_data)
        line2_data = {
            'name': asset.name,
            'move_id': move_id,
            'account_id': asset.account_depr_id.id,
            'debit': amount <0 and -amount or 0.0, 
            'credit': amount >0 and amount or 0.0, 
            'ref': asset.code,
            'period_id': period.id,
            'journal_id': asset.journal_id.id,
            'partner_id': asset.partner_id.id,
            'date': date,
            'asset_id': asset.id     
            }
        id2 = line_obj.create(cr, uid, line2_data)
        self.write(cr, uid, [asset.id],
                   {'move_line_ids': [(4, id2, False),(4, id1, False)]})
        if asset.journal_id.entry_posted:
            move_obj.post(cr, uid, [move_id], context)
        return result

    def _check_date(self, cr, uid, period_id, date, context={}):
        period_obj = self.pool.get('account.period')
        period = period_obj.browse(cr, uid, period_id[0], context)
        if (period.date_start > date) or (period.date_stop < date):
            raise osv.except_osv(_('Error !'), _('Date must be in the period !'))
        if period.state == 'done':
            raise osv.except_osv(_('Error !'), _('Cannot post in closed period !'))
        return period

account_fixed_assets_asset()

class account_move_line(osv.osv):

    _inherit = 'account.move.line'

    _columns = {
        'asset_id': fields.many2one('account.fixed.assets.asset', 'Asset', help = "Assign the asset to move line."),
    }
account_move_line()

class account_fixed_assets_history(osv.osv):

    '''
    Type in history means:
    purchase: Created after purchase for any method
    refund: Created after purchase refund for any method
    reval: Created after purchase for any method
    summary: Created after Summary on demand. Creates Summary of all methods (not implemented yet)
    transfer: Created after changing of location 
    '''

    _name = 'account.fixed.assets.history'
    _description = 'Fixed Assets History'

    _columns = {
        'name': fields.char('History name', size=64, select=1),
        'type': fields.selection([
                ('change','Settings Change'), 
                ('purchase','Purchase'),
                ('refund','Purchase Refund'),
                ('reval', 'Revaluation'),
                ('initial', 'Initial Value'),  
                ('sale','Sale'), 
                ('closing','Closing'),       # not yet used
                ('abandon','Abandonment'), 
                ('suppression','Depr. Suppression'), 
                ('resuming','Depr. Resuming'),
                ('summary','Summary'),
                ('transfer','Transfer')],
            'Entry Type', required=True, readonly=True),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date': fields.date('Date', required=True),
        'asset_id': fields.many2one('account.fixed.assets.asset', 'Asset', required=True),
        'asset_method_id': fields.many2one('account.fixed.assets.method', 'Method', ),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'change_total': fields.float('Total Change', digits_compute=dp.get_precision('Account')),
        'change_expense': fields.float('Expense Change', digits_compute=dp.get_precision('Account')),
        'date_end': fields.date('Ending Date'),    # not used
        'note': fields.text('Note'),
    }
    _defaults = {
        'date': lambda *args: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr, uid,ctx: uid,
    }

    def _history_line(self, cr, uid, type, method, name, total, expense, invoice, note, context={} ):
        if type in ["purchase","initial"]:
            note = _("Parameters set to:") + \
                    _('\n   Number of Intervals: ')+ str(method.method_duration) + \
                    _('\n   Intervals per Year: ')+ str(method.method_freq) + \
                    _('\n   Progressive Factor: ') + str(method.method_progress_factor) + \
                    _('\n   Salvage Value: ') + str(method.value_residual or 0.0)+ \
                    _('\n   Life Quantity: ') + str(method.life or 0.0)+ \
                    _('\n   Intervals Before: ') + str(method.intervals_before or 0.0)+ \
                    "\n" + tools.ustr(note or "")
        history_data = {
             'type': type,
             'asset_method_id': method.id,
             'asset_id' : method.asset_id.id,
             'name': name,
             'partner_id': invoice and invoice.partner_id.id,
             'invoice_id': invoice and invoice.id,
             'change_total': total,
             'change_expense': expense,
#             'method_total': method.value_total,
#             'method_residual': method.value_current,
#             'asset_total': method.asset_id.amount_total,
#             'asset_residual': method.asset_id.amount_residual,
             'note': tools.ustr(note or ""),
             }
        self.create(cr, uid, history_data)

account_fixed_assets_history()

class account_fixed_assets_method_usage(osv.osv):
    
    _name = 'account.fixed.assets.method.usage'
    _description = 'Fixed Assets Method Usage'

    def _get_period(self, cr, uid, context={}):
        periods = self.pool.get('account.period').find(cr, uid)
        return periods and periods[0] or False

    _columns = {
        'asset_method_id': fields.many2one('account.fixed.assets.method',
                                           'Method',required=True,),
        'period_id': fields.many2one('account.period',
                                     'Period', required=True,
                                     help="Select period which usage concerns."),
        'usage': fields.float('Usage',
                              help="Specify usage quantity in selected period."),
    }

    _defaults = {
        'period_id': _get_period,
    }
    
account_fixed_assets_method_usage()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
