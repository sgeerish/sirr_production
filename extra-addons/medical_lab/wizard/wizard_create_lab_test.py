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

from osv import fields, osv
import pooler
from tools.translate import _
import sys

class create_test_report(osv.osv_memory):
	_name='medical.lab.test.create'


	def create_lab_test(self, cr, uid, ids, context={}):
	    
	    data=ids

	    test_request_obj = self.pool.get('medical.patient.lab.test')
	    lab_obj = self.pool.get('medical.lab')

	    test_report_data={}
	    test_cases = []
	    test_obj = test_request_obj.browse(cr, uid, context.get('active_id'), context=context)
	    if test_obj.state == 'tested':
		raise  osv.except_osv(_('UserError'),_('Test Report already created.'))
	    test_report_data['test'] = test_obj.name.id
	    test_report_data['patient'] = test_obj.patient_id.id
	    test_report_data['requestor'] = test_obj.doctor_id.id
	    test_report_data['date_requested'] = test_obj.date
	    
	    for critearea in test_obj.name.critearea:
		test_cases.append((0,0,{'name':critearea.name,
					'sequence':critearea.sequence,
					'normal_range':critearea.normal_range,
					'units':critearea.units.id,
					}))
	    test_report_data['critearea'] = test_cases
	    lab_id = lab_obj.create(cr,uid,test_report_data,context=context)
	    test_request_obj.write(cr, uid, context.get('active_id'), {'state':'tested'})
	    return {
		'domain': "[('id','=', "+str(lab_id)+")]",
		'name': 'Lab Test Report',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'medical.lab',
		'type': 'ir.actions.act_window'
	    }

create_test_report()
