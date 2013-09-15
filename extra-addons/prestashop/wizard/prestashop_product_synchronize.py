# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-TODAY Tech Receptives (<http://www.techreceptives.com>).
#   
#    Authors : Kinner Vachhani  (Tech Receptives)
#    Concept : Parthiv Patel (Tech Receptives)
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

import wizard
import pooler
from tools.translate import _


def do_export(self, cr, uid, data, context):

    prod_pool = pooler.get_pool(cr.dbname).get('product.product')
    #===============================================================================
    #  Getting ids
    #===============================================================================
    prod_ids = prod_pool.search(cr, uid, [('exportable', '=', True), ('updated', '=', False)])
    if data['model'] == 'ir.ui.menu':
        pass
    else:
        prod_ids = list(set.intersection(set(prod_ids),set(data['ids'])))

    return prod_pool.prestashop_sync(cr, uid, prod_ids, context)


#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Product Synchronization">
    <separator string="Product exported" colspan="4" />
    <field name="prod_new"/>
    <field name="prod_update"/>
    <field name="prod_fail" />
</form>'''

_export_done_fields = {
    'prod_new': {'string':'New Produts', 'readonly': True, 'type':'integer'},
    'prod_update': {'string':'Updated Products', 'readonly': True, 'type':'integer'},
    'prod_fail': {'string':'Failed to export Products', 'readonly': True, 'type':'integer'},
}

class wiz_prestashop_product_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_prestashop_product_synchronize('prestashop.products.sync');

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
