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

import time
import datetime
from report import report_sxw

class labtest_report(report_sxw.rml_parse):
        _name = 'report.patient.labtest'
        def __init__(self, cr, uid, name, context):
            super(labtest_report, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
                'get_test': self._get_test,
                'get_doctor' : self.get_doctor,
            })
            
        def _get_test(self, patient, ids={}):
            doctor_id = self.get_doctor_id()
            if doctor_id:
                test_ids = self.pool.get('medical.patient.lab.test').search(self.cr, self.uid, [('doctor_id','=',doctor_id),('patient_id','=',patient.id),('state','=','draft')])
                if test_ids:
                    return self.pool.get('medical.patient.lab.test').browse(self.cr, self.uid, test_ids)
            return []

        def get_doctor_id(self):
            partner_id = self.pool.get('res.partner').search(self.cr,self.uid,[('user_id','=',self.uid)])
            if partner_id:
                physician_id = self.pool.get('medical.physician').search(self.cr, self.uid, [('name','in',partner_id)])
                if physician_id:
                    return physician_id[0]
            return False

        def get_doctor(self):
            partner_id = self.pool.get('res.partner').search(self.cr,self.uid,[('user_id','=',self.uid)])
            if partner_id:
                return self.pool.get('res.partner').read(self.cr, self.uid, partner_id, ['name'])[0]['name']
            else:
                return ''        

report_sxw.report_sxw('report.patient.labtest', 'medical.patient', 'addons/medical_lab/report/labtest.rml', parser=labtest_report, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

