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

class account_fixed_assets_compute(osv.osv_memory):
    """
    Computes the Depreciation entries for fixed assets
    """
    _name = "account.fixed.assets.compute"
    _description = "Compute Fixed Assets"
    _columns = {
        'date': fields.date('Date', required = True, help = "Effective date for accounting move."),
        'period_id': fields.many2one('account.period', \
                            'Period', required = True, help="Calculated period and period for posting."),
        'category_id': fields.many2one('account.fixed.assets.category', 'Asset Category', \
                            required=False, help="If empty all categories assets will be calculated. If you use hierarchical categories all children of selected category be calculated."),
#        'method_id': fields.many2one('account.fixed.assets.method', 'Asset Method', \
#                            required=False, help="If empty all methods will be calculated for assets."), 
    }

    def _get_period(self, cr, uid, context=None):
        """Return default period value"""
        period_ids = self.pool.get('account.period').find(cr, uid)
        return period_ids and period_ids[0] or False

    _defaults = {
      'date': lambda *a: time.strftime('%Y-12-31'),
      'period_id': _get_period,
    }
    
    def compute_assets(self, cr, uid, ids, context=None):
        """
        This function create entries for fixed assets depreciation
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs

        """
        
        obj_asset = self.pool.get('account.fixed.assets.asset')
#        obj_method = self.pool.get('account.fixed.assets.method')
        obj_acc_period = self.pool.get('account.period')
#        obj_acc_fiscalyear = self.pool.get('account.fiscalyear')
#        obj_acc_journal = self.pool.get('account.journal')
#        obj_acc_move_line = self.pool.get('account.move.line')
#        obj_acc_account = self.pool.get('account.account')
#        obj_acc_journal_period = self.pool.get('account.journal.period')

        data = self.read(cr, uid, ids, context=context)[0]
        
        if context is None:
            context = {}
            
        period = obj_asset._check_date(cr, uid, data['period_id'], data['date'], context)
        if data['category_id']:
            asset_ids = obj_asset.search(cr, uid, [('state','=','open'),('category_id','child_of',[data['category_id']])], context=context)
        else:
            asset_ids = obj_asset.search(cr, uid, [('state','=','open')], context=context)
        
        if asset_ids ==[]:
            raise osv.except_osv(_('Warning!'), _('No assets exist for the selection.'))
#        if data[0]['method_id']:
#            method_ids = obj_method.search(cr, uid, [('state','=','open'),('id','=',data[0]['method_id']),('asset_id','in',asset_ids)])
#        else:
#            method_ids = obj_method.search(cr, uid, [('state','=','open'),('asset_id','in',asset_ids)])
#        raise osv.except_osv('User Error!', asset_ids)
        
        ids_create = []
        for asset in obj_asset.browse(cr, uid, asset_ids, context):
            ids_create += obj_asset._compute_entries(cr, uid, asset, period, data['date'], context)
        self.move_ids = ids_create
        
        return {'move_ids': ids_create}

account_fixed_assets_compute()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
