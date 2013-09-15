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

from osv import osv, fields
from tools.translate import _

class account_fixed_assets_location(osv.osv_memory):

    _name = 'account.fixed.assets.location'
    _description = "Fixed Assets Location"

    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'location': fields.char('New Location', size=64, required=True,
                                domain="[('usage','=','internal')]"),
        'note': fields.text('Notes'),
        'state': fields.selection((('init', 'init'),
                                   ('location', 'location'))),
        }

    _defaults = {
        'note': _("Asset transfered because: "),
        'state': 'init',
        }

    def act_asset_location(self, cr, uid, ids, context={}):
        active_id = context.get('active_id', False)
        wiz = self.browse(cr, uid, ids, context)[0]
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset_location = asset_obj._location(cr, uid, active_id, wiz.location.id, wiz.name, wiz.note, context)
        return {
                'type':'ir.actions.act_window_close'
        }

account_fixed_assets_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
