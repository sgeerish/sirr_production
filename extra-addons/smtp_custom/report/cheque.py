from report import report_sxw
import time
import convertion


class cheque(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cheque, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'total_text':self.total_text,
        })

    def total_text(self,montant):
            devis = 'AR'   
            print montant
            text=convertion.trad(montant,devis)
            return text
    
report_sxw.report_sxw('report.account.invoice.cheque',
                      'account.invoice',
                      'addons/smtp_custom/report/cheque.rml',
                      parser=cheque)
    
