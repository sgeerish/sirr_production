# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

pos_form = """<?xml version="1.0"?>
<form string="Create POS">
    <separator colspan="4" string="Select Doctor" />
    <field name="doctor_id"/>
</form>
"""

pos_fields = {
    'doctor_id': {
        'string': 'Doctor',
        'type': 'many2one',
        'relation': 'medical.physician',
        'required': True
    },
}

def _create_pos(obj, cr, uid, data, context):

    pool = pooler.get_pool(cr.dbname)
    pos_obj = pool.get('pos.order')
    patient_obj = pool.get('medical.patient')
    lab_test_obj = pool.get('medical.patient.lab.test')#lab_test_ids

    pos_data={}
    
    patient = patient_obj.browse( cr, uid, data['ids'])[0]
    if patient.name.insurance:
        pos_data['partner_id'] = patient.name.insurance[0].company.id
        pos_data['note']="Patient name :"+patient.name.name+" with insurance No. : "+patient.name.insurance[0].name
    else:
        pos_data['partner_id'] = patient.name.id
    
    lab_test_ids = lab_test_obj.search(cr, uid, [('doctor_id','=',data['form']['doctor_id']),('state','=','draft'),('patient_id','=',patient.id)])
    test_line=[]
    for test in lab_test_obj.browse(cr, uid, lab_test_ids):
        test_line.append((0,0,{'product_id':test.name.product_id.id,
                                'qty':1,
                                'price_unit':test.name.product_id.lst_price}))
    if test_line:
        pos_data['lines'] = test_line
        pos_id = pos_obj.create(cr, uid, pos_data)

        return {
            'domain': "[('id','=', "+str(pos_id)+")]",
            'name': 'POS',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window'
        }
    raise  wizard.except_wizard(_('UserError'),_('No Lab test exist for selected Dr.'))

class make_lab_pos(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': pos_form,
                'fields': pos_fields,
                'state': [
                    ('end', 'Cancel'),
                    ('create_pos', 'Create POS')
                ]
            }
        },
        'create_pos': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _create_pos,
                'state': 'end'
            }
        },
    }

make_lab_pos("patient.create_lab_pos")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

