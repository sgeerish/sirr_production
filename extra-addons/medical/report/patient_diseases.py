# -*- coding: utf-8 -*-

import time
import datetime
from report import report_sxw

class diseases_report(report_sxw.rml_parse):
        _name = 'report.patient.diseases'
        def __init__(self, cr, uid, name, context):
            super(diseases_report, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
            })

report_sxw.report_sxw('report.patient.diseases', 'medical.patient', 'addons/medical/report/patient_diseases.rml', parser=diseases_report, header=True )



