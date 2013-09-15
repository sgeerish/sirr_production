# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-TODAY Tech-Receptives Solutions Pvt. Ltd.
#                            (<http://www.techreceptives.com>)
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

from osv import fields, osv

class product_sync_wizard(osv.osv_memory):
    
    _name = "prodcut.sync.wizard"
    _description = ""
    _columns = {
                'shop_ids': fields.many2many('sale.shop',
                         'sale_shop_product_tble', 'product_id', 'shop_id',
                         'Shops', required=True, help="Select your shop name"),                   
               }

    def export_product(self, cr, uid, ids, context=None):
        
        for self_obj in self.browse(cr, uid, ids, context=context):
            
            self.pool.get('sale.shop').export_product(cr, uid,[x.id for x in \
                                       self_obj.shop_ids],
                                       context=context,
                                       export_ids=context.get('active_ids', []))
                                                                    
        return {'type': 'ir.actions.act_window_close'}

product_sync_wizard()
