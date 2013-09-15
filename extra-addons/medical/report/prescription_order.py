# -*- coding: utf-8 -*-

import time
import datetime
from report import report_sxw

class prescription_report(report_sxw.rml_parse):
        _name = 'report.prescription.order'
        def __init__(self, cr, uid, name, context):
            super(prescription_report, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
            })

report_sxw.report_sxw('report.prescription.order', 'medical.prescription.order', 'addons/medical/report/prescription_order.rml', parser=prescription_report, header=False )



