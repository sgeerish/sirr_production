from report import report_sxw
import convertion
import time


# this bit is basically a copy of the stuff
# in the regular sale order module.
# I can't just import that code because it causes
# the sale.order report to get registered again
# causing it to complain.
# otherwise I’d do this - from addons.sale.report import order 
class cheque_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(cheque_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'total_text':self.total_text,
            
        })
        
    def total_text(self,montant):
            devis = 'AR'   
            print montant
            text=convertion.trad(montant,devis)
            return text        

report_sxw.report_sxw('report.cheque.print.bni', 'cheque.print', 'addons/cheque_print/report/bni.rml', parser=cheque_print, header="external")
