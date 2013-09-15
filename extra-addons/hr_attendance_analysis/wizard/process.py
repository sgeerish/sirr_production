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
import netsvc
import pooler

from time import mktime
import datetime as dt
from .. import timeutils as tu


_result_form = '''<?xml version="1.0"?>
     <form string="Process final status">
     <field name="count" readonly="True"/>
     <newline/>
     <field name="errors" size="128" readonly="True"/>
     </form>'''

_result_fields = {
    'count': {'string': 'Number of generated items', 'type': 'integer', 'required': True,
             'readonly': True},
    'errors': {'string': 'Errors', 'type': 'text', 'required': True,
             'readonly': True},
}

def _get_time_start_attendance(self, cr, uid, data, context):
    cr.execute(
"""
SELECT DATE_TRUNC('DAY', MIN(A.name))
   FROM hr_attendance AS A
"""
    )
    time_start = cr.fetchall()

    if len(time_start) == 0:
        return False
    return time_start[0][0]

def _get_time_start_day(self, cr, uid, data, context):
    cr.execute(
"""
SELECT DATE_TRUNC('DAY', MAX(A.date) + interval '1 days')
   FROM hr_aa_journal AS A
"""
    )
    time_start = cr.fetchall()

    if time_start == [(None,)]:
        return _get_time_start_attendance(self, cr, uid, data, context)
    return time_start[0][0]

def _process(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    r = {'errors': ''}

    # Process day
    time_start = _get_time_start_day(self, cr, uid, data, context)
    count = 0
    if time_start:
        count = pool.get('hr.aa.journal').build(cr, uid, time_start, tu.dt2s(tu.datetime.today()), context=context)
    else:
        r['errors'].append('Must be any attendance to generate analysis data')

    return { 'errors': '\n'.join(r['errors']), 'count': count }

class wiz_attendance_process(wizard.interface):
    states={
        'init':{
            'actions':[_process],
            'result':{
                'type': 'form',
                'arch': _result_form,
                'fields': _result_fields,
                'state': [('end','OK')],
            },
        },
    }

wiz_attendance_process('hr.aa.attendance_process')

