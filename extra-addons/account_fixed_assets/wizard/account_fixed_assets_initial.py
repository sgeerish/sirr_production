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

class account_fixed_assets_initial(osv.osv_memory):

    _name = 'account.fixed.assets.initial'
    _description = "Initial Records Fixed Assets"

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        ids = self.pool.get('account.period').find(cr, uid, context=context)
        return ids[0] and ids[0] or False    

    _columns = {
        'date': fields.date('Date', required=True, help="Effective date for posting."),
        'period_id': fields.many2one('account.period',string='Period',
                                     required=True, help="Period for posting. \
                                     Consider which period to use for this posting. \
                                     It should be probably some additional period before current depreciation start."),
        'name': fields.char('Description', size=64),
        'value': fields.float('Base Value', help="Initial Base Value of method."),
        'expense_value': fields.float('Expense Value', help="Initial Value of method expenses.\
        There are sum of depreciations made before this system asset management."),
        'intervals_before': fields.integer('Intervals Before', help="Number of intervals calculated already before asset is managed in this system."),
        'acc_impairment': fields.many2one('account.account', string='Impairment Account', required=True, help="Counter account for base value."),
        'note': fields.text('Notes'),
        'state': fields.selection((('init', 'init'),
                                   ('initial', 'initial'))),        
        }

    _defaults = {
        'note': _("Inital values for asset: "),
        'date': time.strftime('%Y-%m-%d'),
        'period_id': _get_period,
        }

    def act_asset_initial(self, cr, uid, data, context={}):
        active_id = context.get('active_id', False)
        wiz = self.browse(cr, uid, ids, context)[0]
        asset_obj = self.pool.get('account.fixed.assets.asset')
        method_obj = self.pool.get('account.fixed.assets.method')
        asset = asset_obj.browse(cr, uid, active_id, context)
        method = asset.method_id
        method_obj._initial(cr, uid, method, wiz.period_id.id, wiz.date, wiz.value, wiz.expense_value, \
                            wiz.acc_impairment, wiz.intervals_before, wiz.name, wiz.note, asset.id, context)
        return {
                'type':'ir.actions.act_window_close'
        }

account_fixed_assets_initial()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
