# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from osv import osv, fields
from tools.translate import _

class account_fixed_assets_reval(osv.osv_memory):

    _name = 'account.fixed.assets.reval'
    _description = "Revalue Fixed Assets"

    def _asset_default(self, cr, uid, context=None):
        if context is None:
            context = {}
        asset_id = context.get('active_id')
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset = asset_obj.browse(cr, uid, asset_id, context)
        acc_expense = asset.category_id and asset.category_id.account_expense_id and asset.category_id.account_expense_id.id
#        defaults = method_obj.get_defaults(cr, uid, method.method_type.id, asset_category_id, context)
#        acc_impairment = defaults and defaults.account_impairment_id and defaults.account_impairment_id.id or False
        return acc_expense

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        ids = self.pool.get('account.period').find(cr, uid, context=context)
        return ids[0] and ids[0] or False

    _columns = {
        'date': fields.date('Date', required=True,
                            help="Efective date for accounting move."),
        'period_id': fields.many2one('account.period', 'Period', required=True,
                                     help="Calculated period and period for posting."),
        'name': fields.char('Description', size=64, required=True),
        'value': fields.float('Increasing Base Value',
                              help="Value to be added to method base value. \
                              In Direct method it is increasing of book value. \
                              In Indirect method it is increasing of cost basis. Negative value means decreasing."),
        'expense_value': fields.float('Increasing Expense Value',
                                      help="Value to be added to asset expenses. \
                                      Used only in indirect method. In direct method ignored."),
        'acc_impairment': fields.many2one('account.account', 'Impairment Account', required=True,
                                          help="Account for impairment loss amount."),
        'note': fields.text('Notes'),
        'state': fields.selection((('init', 'init'),
                                   ('reval', 'reval'))),
        }

    _defaults = {
        'note': _("Asset revalued because: "),
        'date': time.strftime('%Y-%m-%d'),
        'acc_impairment': _asset_default,
        'period_id': _get_period,
        'state': 'init',
        }

    def act_asset_reval(self, cr, uid, ids, context={}):
        wiz = self.browse(cr, uid, ids)[0]
        active_id = context.get('active_id',False)
        method_obj = self.pool.get('account.fixed.assets.method')
        asset = self.pool.get('account.fixed.assets.asset').browse(cr, uid, active_id, context)
        method = method_obj.browse(cr, uid, asset.method_id.id, context)
        method_obj._reval(cr, uid, method, wiz.period_id, wiz.date, wiz.value, wiz.expense_value,\
            wiz.acc_impairment, wiz.name, wiz.note, context)
        return {
                'type':'ir.actions.act_window_close'
        }

account_fixed_assets_reval()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
