from report import report_sxw
import time


# this bit is basically a copy of the stuff
# in the regular sale order module.
# I can't just import that code because it causes
# the sale.order report to get registered again
# causing it to complain.
# otherwise I’d do this - from addons.sale.report import order 
class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw('report.sale.collection_docket', 'sale.order', 'addons/module/report/collection_docket.rml', parser=order, header="external")
