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

def _attendance_reason_compute(self,cr,uid,data,context=None):
    pool = pooler.get_pool(cr.dbname)
    att = pool.get('hr.aa.attendance')

    att.compute_reason_rules(cr, uid, data['ids'], context=context)

    return {}

class wiz_attendance_reason_compute(wizard.interface):
    states={
        'init':{
        'actions':[],
        'result':{
            'type':'action',
            'action': _attendance_reason_compute,
            'state': 'end',
            }
        }
    }

wiz_attendance_reason_compute('hr.aa.attendance_reason_compute')

