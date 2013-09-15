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

from osv import osv, fields
from tools.translate import _

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    
    def line_get_convert(self, cr, uid, x, part, date, context={}):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context)
        res['asset_category_id'] = x.get('asset_category_id', False)
        return res

    def _refund_cleanup_lines(self, cr, uid, lines):
        for line in lines:
            if 'asset_category_id' in line:
                line['asset_category_id'] = line.get('asset_category_id', False) and line['asset_category_id'][0]
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        return res

    def action_move_create(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_move_create(cr, uid, ids, *args)
        
        asset_obj = self.pool.get('account.fixed.assets.asset')
        category_obj = self.pool.get('account.fixed.assets.category')
        method_obj = self.pool.get('account.fixed.assets.method')
        context = {}
        for inv in self.browse(cr, uid, ids):
            if inv.type == "out_refund":
                continue
            for line in inv.invoice_line:
                if not line.asset_category_id:
                    continue

                category_id = line.asset_category_id.id
                if category_id is None:
                    raise osv.except_osv(_('Error !'), _('You have to select/create first a Fixed Assets category!'))
                category = category_obj.browse(cr, uid, category_id)
                
                method_id = category.method_id.id
                if not method_id:
                    raise osv.except_osv(_('Error !'), _('You have to select/create first a Fixed Assets method for category!'))
                method = method_obj.browse(cr, uid, method_id)

                asset = {
                    'name': line.name,
                    'invoice_id': line.invoice_id.id,
                    'move_id': line.invoice_id.move_id.id,
                    'category_id': category.id,
                    'account_asset_id': category.account_asset_id.id,
                    'account_depr_id': category.account_depr_id.id,
                    'account_expense_id': category.account_expense_id.id,
                    'method_id': category.method_id.id,
                    'date': line.invoice_id.date_invoice,
                    'period_id': line.invoice_id.period_id.id,
                    'partner_id': line.invoice_id.partner_id.id,
                    'company_id': line.invoice_id.company_id.id,
                    'currency_id': line.invoice_id.currency_id.id,
                    'product_id': line.product_id.id,
                    ### TODO tax treatment and 
                    ### multiple purchases (several identical items)
                    'value_total': line.price_unit,
                    'value_current': line.price_unit,
###                 TODO journal_id default for FA, created at install  
###                    'journal_id': line.invoice_id.partner_id.id,
                    'method_progress_factor': method.method_progress_factor,
                    'method_duration': method.method_duration,
                    'method_freq': method.method_freq
                }

                if line.invoice_id.type == "in_invoice":
                    asset_type = "purchase"
                elif line.invoice_id.type == "in_refund":
                    assset_type = "refund"
                elif line.invoice_id.type == "out_invoice":
                    asset_type = "sale"
                if asset_type in ["purchase","refund"]:
                    if category.state=='draft':
                        category_obj.validate(cr, uid, [category_id])
#                    raise osv.except_osv('Error !', asset) 
    
                    asset_id = asset_obj.create(cr,uid,asset,context=context)
                        
#                    base = (type == 'purchase') and line.price_subtotal or - line.price_subtotal
#                    expense = 0.0
#                elif type == "sale":
#                    if not category.account_residual_id:
#                        raise osv.except_osv(_('Error !'), _('Product "%s" is assigned to Asset category "%s". But this category has no Sale Residual Account to make asset moves.')%(line.product_id.name, category.name,)) 
#                    elif line.asset_category_id.state in ["closed","draft"]:
#                        raise osv.except_osv(_('Error !'), _('You cannot assign Product "%s" to Asset category "%s". This category is in Draft state or is inactive (sold or abandoned).')%(line.product_id.name, category.name,)) 
#                    direct = (category.account_asset_id.id == category.account_expense_id.id)
#                    base = direct and - category.value_current or -category.value_total
#                    expense = not direct and -(category.value_total - category.value_current) or False
#                    category_obj._post_3lines_move(cr, uid, category= category, period=line.invoice_id.period_id, \
#                            date = line.invoice_id.date_invoice, acc_third_id = category.account_residual_id.id, \
#                            base = base, expense = expense,)
#                    category_obj._close(cr, uid, category)
#                note = _("Product name: ") + line.product_id.name + ' ['+line.product_id.code+ \
#                        _("]\nInvoice date: ") + line.invoice_id.date_invoice + \
#                        _("\nPrice: ") + str(line.price_subtotal)
#                self.pool.get('account.fixed.assets.history')._history_line(cr, uid, type, category, line.product_id.name, base, expense, \
#                            line.invoice_id, note, )
        return  res

account_invoice()

class account_invoice_line(osv.osv):
    
    _inherit = 'account.invoice.line'
    
    _columns = {
        'asset_track': fields.boolean('Track as Asset', help="Track this purchased item as asset."),
        'asset_category_id': fields.many2one('account.fixed.assets.category', 'Asset Category',
                                             help="Select the asset category if you wish to assign the purchase invoice line to fixed assets."),
    }
    
    _defaults = {
                'asset_track': lambda obj, cr, uid, context: False,           
    }

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=context)
        res['asset_category_id'] = line.asset_category_id and line.asset_category_id.id or False
        return res

    def asset_category_id_change(self, cr, uid, ids, asset_category_id, type, context={}):
        result = {}
        if asset_category_id and type in ["in_invoice","in_refund"]:
            result['account_id'] = self.pool.get('account.fixed.assets.category').browse(cr, uid, asset_category_id,{}).account_asset_id.id
        return {'value': result}
    
    def track_asset(self, cr, uid, ids, asset_track, context={}):
        result= {}
        if asset_track and asset_track == False:
            result['asset_category_id'] = ''
        return {'value': result}
    
account_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

