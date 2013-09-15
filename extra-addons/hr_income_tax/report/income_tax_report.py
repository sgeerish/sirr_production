import time
import locale
import datetime
from report import report_sxw
import time
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

class income_tax_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(income_tax_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_other_allowance' :self.get_other_allowance,
            'get_other_income' :self.get_other_income,
            'get_second_amt':self.get_second_amt,
            'get_third_amt':self.get_third_amt,
            'get_other_ded_80cc' :self.get_other_ded_80cc,
            'get_other_ded_6a' :self.get_other_ded_6a,
            'get_surcharge_amt' :self.get_surcharge_amt,
            'get_total_house_amt' :self.get_total_house_amt,
            'get_document':self.get_document,
        })

    def get_document(self,obj):
        done_l=[]
        result=[]
        res={}
        if obj.docs:
            for doc in obj.docs:
                res = {}
                if doc.type:
                    s_id = self.pool.get('document.proof.type').search(self.cr,self.uid,[('shortcut','=',doc.type)])
                    name_l = self.pool.get('document.proof.type').read(self.cr,self.uid,s_id,['name'])
                    type = name_l[0]['name']
                else:
                    other_id = self.pool.get('document.proof.type').search(self.cr,self.uid,[('name','=','Other')])
                    other_l = self.pool.get('document.proof.type').read(self.cr,self.uid,other_id,['name'])
                    type =  other_l[0]['name']
                if type not in done_l:
                    done_l.append(type)
                    res['name'] = type
                    res['count']= 1
                    result.append(res)
                else:
                    for r in result:
                        if r['name'] == type:
                            r['count'] += 1
        return result

    def  get_other_allowance(self,obj):
         res={}
         other_total = 0.00
         other_total = (obj.professional_tax + obj.med_reimbersement + obj.lta 
                        + obj.le + obj.vma + obj.ea + obj.aa + obj.ua + obj.eda + obj.ha + obj.na)
         res['other_total']=other_total
         return res
     
    def  get_other_income(self,obj):
         res={}
         other_result_amt = 0.00
         if obj.other_income:
             for other in obj.other_income:
                other_result_amt += other.amt
         res['other_total']=other_result_amt
         return res

    def get_second_amt(self,obj):
        res = {
               'final_amt':0.00
               }
        b_sal=0.00
        for o in obj.employee.sal_ids:
            b_sal += o.basic
        if obj.less.rent_paid_hra > 0.00:
            res['final_amt'] = obj.less.rent_paid_hra - (b_sal *(obj.less.ded_pec2/100))
            if res['final_amt'] < 0.00:
                res['final_amt']= 0.00
        return res

    def  get_third_amt(self,basic_hra,per):
         res={}
         res['amount']=basic_hra * (per/100)
         return res

    def  get_other_ded_80cc(self,obj):
         res={}
         other_result_amt = 0.00
         if obj.other_ded:
             for other in obj.other_ded:
                other_result_amt += other.amt
         res['other_ded']=other_result_amt
         return res

    def  get_other_ded_6a(self,obj):
         res={}
         other_result_amt = 0.00
         if obj.other_ded6a:
             for other in obj.other_ded6a:
                other_result_amt += other.amt
         res['other_ded_6a']=other_result_amt
         return res

    def  get_surcharge_amt(self,obj):
         res={}
         amount = 0.00
         if obj.surcharge:
             if obj.surcharge.sur_amt < obj.tax_on_tol:
                 amount = (obj.tax_on_tol * (obj.surcharge.perc/100))
         res['amount']=amount
         return res
     
    def  get_total_house_amt(self,obj):
         res={}
         result_amt = 0.00
         if obj.inc_h_pro:
             for obj_h in obj.inc_h_pro:
                result_amt += obj_h.total_net_amt
         if result_amt > 0.0:
             res['amount']=result_amt
         else:
             res['amount'] = 0.00
         return res
        
report_sxw.report_sxw('report.income.tax.report', 'cal.income.tax', 'hr_cal_income_tax/report/income_tax_report.rml', parser=income_tax_report,header=False)
       
       
    