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

class account_fixed_assets_abandon(osv.osv_memory):

    _name = 'account.fixed.assets.abandon'
    _description = "Abandon Fixed Assets"

    def _asset_default(self, cr, uid, context=None):
        if context is None:
            context = {}
#        method_obj = self.pool.get('account.fixed.assets.method')
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset = asset_obj.browse(cr, uid, context.get('active_id'), context)
        acc_abandon = asset.category_id.account_depr_id.id
#        asset_category_id = asset.category_id and \
#                            asset.category_id.id or False
#        defaults = method_obj.get_defaults(cr, uid, asset.method.method_type.id, asset_category_id, context)
#        acc_abandon = defaults and defaults.account_abandon_id and \
#                      defaults.account_abandon_id.id or False
        return acc_abandon

    def _get_period(self, cr, uid, context=None):
        if context is None:
            context = {}
        ids = self.pool.get('account.period').find(cr, uid, context=context)
        return ids[0] and ids[0] or False

    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'date': fields.date('Date', required=True, help="Efective date for accounting move."),
        'period_id': fields.many2one('account.period', string='Period', required=True, help="Calculated period and period for posting."),
        'whole_asset': fields.boolean('All Methods', help="Abandon all methods of this asset."),
        'acc_abandon': fields.many2one('account.account', string='Abandon Account', required=True, help='Account for asset loss amount.'),
        'note': fields.text('Notes'),
        'state': fields.selection((('init', 'init'),
                                   ('abandon', 'abandon'))),        
        }

    _defaults = {
        'name': '/',
        'note': _("Asset abandoned because: "),
        'date': time.strftime('%Y-%m-%d'),
        'acc_abandon': _asset_default,
        'period_id': _get_period,
        'state': 'init',
        }

    def act_asset_abandon(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wiz = self.browse(cr, uid, ids, context)[0]
        asset_id = context.get('active_id')
        method_obj = self.pool.get('account.fixed.assets.method')
        met = method_obj.browse(cr, uid, asset_id, context)
        methods = wiz.whole_asset and met.asset_id.method_ids or [met]
        method_obj._abandon(cr, uid, methods, wiz.period_id, wiz.date,\
                            wiz.acc_abandon, wiz.name, wiz.note, asset_id, context)
        return self.write(cr, uid, ids, {'state': 'abandon'})

account_fixed_assets_abandon()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
