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
#    GNU General Public License for more days.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import datetime
import wizard
from tools.translate import _

setup_form = '''<?xml version="1.0"?>
     <form string="Setup report">
         <field name="date_from"/>
         <field name="date_to"/>
     </form>'''

def _calc_quincena():
    date = datetime.date.today()
    sunday = date - datetime.timedelta(date.weekday()+1)
    quincena_begin = sunday - datetime.timedelta(7)
    quincena_end   = sunday + datetime.timedelta(7)
    return (quincena_begin, quincena_end)

setup_fields = {
    'date_from': {'string': 'First day', 'type': 'date',
                  'default':lambda *a: _calc_quincena()[0].strftime('%Y-%m-%d'),
                  'required':True },
    'date_to': {'string': 'Last day', 'type': 'date',
                'default':lambda *a: _calc_quincena()[1].strftime('%Y-%m-%d'),
                'required':True },
}

def _check_data(self, cr, uid, data, *args):
    if data['form']['date_from'] > data['form']['date_to']:
        raise wizard.except_wizard(_('Error!'),\
                                   _('Begin date must be before the end day'))
    data['form']['emp_ids'] = data['ids']
    return data['form']

class wiz_print_journal_report(wizard.interface):
    states={
        'init':{
        'actions':[],
        'result':{
            'type':'form',
            'arch':setup_form,
            'fields':setup_fields,
            'state':[('end','Cancel'),('print','Print')]
            }
        },
       'print':{
        'actions':[ _check_data ],
        'result':{
            'type':'print',
            'report':'hr.aa.print_journal_report',
            'state': 'end',
            }
        },
    }

wiz_print_journal_report('hr.aa.print_journal_report')

