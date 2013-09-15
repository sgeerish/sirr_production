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

    tax_pool = pooler.get_pool(cr.dbname).get('account.tax')
    #===============================================================================
    #  Getting ids
    #===============================================================================
    tax_ids = tax_pool.search(cr, uid, [])
#    if data['model'] == 'ir.ui.menu':
#        categ_ids = categ_pool.search(cr, uid, [('exportable', '=', True)])
#        categ_ids = categ_pool.search(cr, uid, [])
#        pass
#    else:
#        tax_ids = list(set.intersection(set(categ_ids),set(data['ids'])))

    return tax_pool.prestashop_sync(cr, uid, tax_ids, context)


#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Tax Synchronization">
    <separator string="Taxes imported" colspan="4" />
    <field name="tax_new"/>
    <field name="tax_update"/>
    <field name="tax_del" />
</form>'''

_export_done_fields = {
    'tax_new': {'string':'New Tax', 'readonly': True, 'type':'integer'},
    'tax_update': {'string':'Updated Tax', 'readonly': True, 'type':'integer'},
    'tax_del': {'string':'Tax deleted', 'readonly': True, 'type':'integer'},
}

class wiz_prestashop_tax_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_prestashop_tax_synchronize('prestashop.tax.sync');

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
