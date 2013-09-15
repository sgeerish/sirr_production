# -*- coding: utf-8 -*-

import time
import datetime
from report import report_sxw

class vaccination_report(report_sxw.rml_parse):
        _name = 'report.patient.vaccinations'
        def __init__(self, cr, uid, name, context):
            super(vaccination_report, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
            })

report_sxw.report_sxw('report.patient.vaccinations', 'medical.patient', 'addons/medical/report/patient_vaccinations.rml', parser=vaccination_report, header=True )



