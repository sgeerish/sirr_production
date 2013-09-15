# -*- coding: utf-8 -*-

import time
import datetime
from report import report_sxw

class medication_report(report_sxw.rml_parse):
        _name = 'report.patient.medications'
        def __init__(self, cr, uid, name, context):
            super(medication_report, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
            })

report_sxw.report_sxw('report.patient.medications', 'medical.patient', 'addons/medical/report/patient_medications.rml', parser=medication_report, header=True )



