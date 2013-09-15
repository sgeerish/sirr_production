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

import time
import wizard

setup_form = '''<?xml version="1.0"?>
     <form string="Setup report">
     <field name="date_from"/>
     <field name="date_to"/>
     </form>'''

setup_fields = {
    'date_from': {'string': 'Start day of report', 'type': 'date', 'default':lambda *a: time.strftime('%Y-%m-%d'), 'required':True },
    'date_to': {'string': 'End day of report', 'type': 'date', 'default':lambda *a: time.strftime('%Y-%m-%d'), 'required':True },
}

class wiz_registration_quality_report(wizard.interface):
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
        'actions':[ ],
        'result':{
            'type':'print',
            'report':'clock_reader.registration_quality_report',
            'state': 'end',
            }
        },
    }

wiz_registration_quality_report('clock_reader.registration_quality_report')

