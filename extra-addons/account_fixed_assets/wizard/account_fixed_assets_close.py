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

class account_fixed_assets_close(osv.osv_memory):

    _name = 'account.fixed.assets.close'
    _description = "Close Fixed Assets"
   
    def act_asset_supress(self, cr, uid, ids, context=None):
        asset_obj = self.pool.get('account.fixed.assets.asset')
        method_obj = self.pool.get('account.fixed.assets.method')
        
        if context is None:
            context = {}
        wiz = self.browse(cr, uid, ids)[0]
        asset = asset_obj.browse(cr, uid, context.get('active_id'), context)
        methods = wiz.whole_asset and [asset.method_id] or []
        method_obj._suppress(cr, uid, methods, wiz.name, wiz.note, context)
        return {
                'type':'ir.actions.act_window_close'
        }        

    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'whole_asset': fields.boolean('All Methods'),
        'note': fields.text('Notes'),
        'state': fields.selection((('init', 'init'),
                                   ('supress', 'supress'))),
        }

    _defaults = {
        'note': _('Suppressed because:'),
        'state': 'init',
        }

account_fixed_assets_close()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
