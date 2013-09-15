# -*- encoding: utf-8 -*-
##############################################################################
#
#    Clock Reader for OpenERP
#    Copyright (C) 2004-2009 Moldeo Interactive CT
#    (<http://www.moldeointeractive.com.ar>). All Rights Reserved
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

# Agregar aqui mas modelos y en ../clock.py
connect_form = '''<?xml version="1.0"?>
     <form string="Start read attendance from clocks">
     <field name="override"/>
     <newline/>
     <field name="unknown"/>
     <newline/>
     <field name="complete"/>
     <newline/>
     <field name="tolerance"/>
     <newline/>
     <field name="ignore_signs"/>
     </form>'''

connect_fields = {
    'override': {'string': 'Override clock options with this options', 'type': 'boolean'},
    'unknown': {'string': 'Create unknown employee', 'type': 'boolean'},
    'complete': {'string': 'Complete attendance', 'type': 'boolean'},
    'tolerance': {'string': 'Tolerance between equivalent entries', 'type': 'integer'},
    'ignore_signs': {'string': 'Ignore signs in/outs', 'type': 'boolean'},
}

def _get_actions(self, cr, uid, data, context=None):
    return {'tolerance': 60*5}

read_form = '''<?xml version="1.0"?>
     <form string="Final read status">
     <field name="count" readonly="True"/>
     <newline/>
     <field name="errors" size="128" readonly="True"/>
     </form>'''

read_fields = {
    'count': {'string': 'Number of Items loaded', 'type': 'integer', 'required': True,
             'readonly': True},
    'errors': {'string': 'Errors', 'type': 'text', 'required': True,
             'readonly': True},
}

_negative_action = {
    'sign_in': 'sign_out',
    'sign_out': 'sign_in',
}

def _read_clock(self, cr, uid, data, context=None):
    pool = pooler.get_pool(cr.dbname)
    clock_pool = pool.get('clock_reader.clock')

    if data['form']['override']:
        create_unknown_employee = data['form']['unknown']
        complete_attendance = data['form']['complete']
        tolerance = data['form']['tolerance']
        ignore_signs = data['form']['ignore_signs']
    else:
        create_unknown_employee = None
        complete_attendance = None
        tolerance = None
        ignore_signs = None
    print data
    if len(data['ids'])==0:
        clock_ids = clock_pool.search(cr, uid, [], context=context)
    else:
        clock_ids=data['ids']
    ret = clock_pool.load_attendances(cr, uid, clock_ids,
                          create_unknown_employee=create_unknown_employee,
                          complete_attendance=complete_attendance,
                          tolerance=tolerance,
                          ignore_sign_inout=ignore_signs)

    return {'count': ret['count'], 'errors': '\n'.join(ret['errors'])}

class wiz_read_clock(wizard.interface):
    states={
        'init':{
        'actions':[_get_actions],
        'result':{
            'type':'form',
            'arch':connect_form,
            'fields':connect_fields,
            'state':[('end','Cancel'),('read','Read')]
            }
        },
       'read':{
        'actions':[_read_clock],
        'result':{
            'type':'form',
            'arch':read_form,
            'fields':read_fields,
            'state':[('end','OK')]
            }
        },
    }

wiz_read_clock('clock_reader.read_clock')

