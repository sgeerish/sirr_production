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
import pdb

class account_fixed_assets_modify(osv.osv_memory):

    _name = 'account.fixed.assets.modify'
    _description = "Modify Fixed Assets"

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}    
    
    def _get_method_duration(self, cr, uid, context={}):
        import pdb
        active_id = context.get('active_id', False)
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset = asset_obj.browse(cr, uid, active_id)
        method = asset.method_id
        return method.method_duration
    
    def _get_freq(self, cr, uid, context={}):
        active_id = context.get('active_id', False)
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset = asset_obj.browse(cr, uid, active_id)
        method = asset.method_id
        return method.method_freq

    def _get_factor(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        asset_obj = self.pool.get('account.fixed.assets.asset')
        asset = asset_obj.browse(cr, uid, active_id)
        method = asset.method_id        
        return method.method_progress_factor

    def act_asset_modif(self, cr, uid, data, context={}):
        active_id = context.get('active_id', False)
        wiz = self.browse(cr, uid, ids, context)[0]
        asset_obj = self.pool.get('account.fixed.assets.asset')
        method = asset_obj.browse(cr, uid, active_id, context).method_id
        method_obj._modif(cr, uid, method, wiz.method_duration, wiz.method_freq, wiz.method_progress_factor, \
                          wiz.value_residual, wiz.life, wiz.name, wiz.note, context)
        return {
                'type':'ir.actions.act_window_close'
        }        

    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'method_duration': fields.integer('Number of Intervals'),
        'method_freq': fields.integer('Intervals per Year'),
        'method_progress_factor': fields.float('Progressive Factor'),
        'value_residual': fields.float('Salvage Value'),
        'life': fields.float('Life Quantity'),
        'note': fields.text('Notes'),
        'state': fields.selection((('init', 'init'),
                                   ('modify', 'modify'))),        
        }

    _defaults = {
        'state': 'init',
        'name': _("Modification of "),
        'method_duration': _get_method_duration,
        }

account_fixed_assets_modify()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
