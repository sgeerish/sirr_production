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

    categ_pool = pooler.get_pool(cr.dbname).get('product.category')
    #===============================================================================
    #  Getting ids
    #===============================================================================
    categ_ids = categ_pool.search(cr, uid, [('updated', '=', False)])
    if data['model'] == 'ir.ui.menu':
        pass
    else:
        categ_ids = list(set.intersection(set(categ_ids),set(data['ids'])))

    return categ_pool.prestashop_sync(cr, uid, categ_ids, context)


#===============================================================================
#   Wizard Declaration
#===============================================================================

_export_done_form = '''<?xml version="1.0"?>
<form string="Categories Synchronization">
    <separator string="Categories exported" colspan="4" />
    <field name="categ_new"/>
    <field name="categ_update"/>
    <field name="categ_fail" />
</form>'''

_export_done_fields = {
    'categ_new': {'string':'New Categories', 'readonly': True, 'type':'integer'},
    'categ_update': {'string':'Updated Categories', 'readonly': True, 'type':'integer'},
    'categ_fail': {'string':'Failed to export Categories', 'readonly': True, 'type':'integer'},
}

class wiz_prestashop_category_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [do_export],
            'result': {'type': 'form', 'arch': _export_done_form, 'fields': _export_done_fields, 'state': [('end', 'End')] }
        }
    }
wiz_prestashop_category_synchronize('prestashop.categories.sync');

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
