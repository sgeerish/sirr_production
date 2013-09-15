from report import report_sxw
import time
import convertion
import datetime

class bulletin(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bulletin, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'total_text':self.total_text,
            'gross_wage_line' : self.gross_wage_line,
            'cotisation_line' : self.cotisation_line,
            'get_total' : self.get_total,
            'get_holidays':self.get_holidays
        })

    def total_text(self,montant):
            devis = 'Ariary'   
            return convertion.trad(montant, devis)


    def gross_wage_line(self, salary_line_ids) :
        list=[]
        for line in salary_line_ids :
            if line.type == 'brute' and line.afficher:
                if line.deductible:
                    gain=0
                    retenu=float(line.subtotal_employee)
                else:
                    gain=float(line.subtotal_employee)
                    retenu=0
                    
                dict={'name' : line.name,
                      'base' : line.base,
                      'rate_employee' : float(line.rate_employee),
                      'gain' : gain,
                      'retenu': retenu,
                      }
                list.append(dict)
        return list
    
            
    def cotisation_line(self, salary_line_ids):    
        list=[]
        for line in salary_line_ids :
            if line.deductible and line.afficher and line.type <> 'brute' :
                dict={'name' : line.name,
                      'base' : line.base,
                      'rate_employee' : line.rate_employee,
                      'subtotal_employee' : line.subtotal_employee,
                      'rate_employer' : line.rate_employer,
                      'subtotal_employer' : line.subtotal_employer,
                      } 
                list.append(dict)
        return list

    def get_holidays(self,employee_id,period_id):
        holidays=self.pool.get('hr.holidays').search(self.cr, self.uid,[('employee_id','=',employee_id.id)])
        holidays=self.pool.get('hr.holidays').browse(self.cr, self.uid,holidays)
        text='Conges:\n'
        data={}
        list=[]
        # conges pris ce mois
        taken=0
        given=0
        for holiday in holidays:
            if datetime.datetime.strptime(holiday.date_from[:10],'%Y-%m-%d').month ==datetime.datetime.strptime(period_id.date_start,'%Y-%m-%d').month:
                if holiday.type=='add':
                    given+=holiday.number_of_days
            if holiday.date_from>=period_id.date_start and holiday.date_to<=period_id.date_stop and holiday.type!='add':
                taken+=holiday.number_of_days*-1
        dict={'Conges Pris':taken}
        text='Conges Pris :'+taken+'\n'
        list.append(dict)
        text='Conges Attribue :'+given+'\n'
        dict={'Conges Attribue':given}
        list.append(dict)

        # balance de conge
        for holiday in holidays:
            if holiday.date_to<=period_id.date_stop:
                name=holiday.holiday_status_id.name+' restant'
                if name in data:
                    data[name]+=holiday.number_of_days
                else:
                    data[name]=holiday.number_of_days
        for key,dat in data.iteritems():
            dict={}
            dict={key:dat}
            text=key+':'+dat
            list.append(text)
        #return list
        return text

    def get_total(self,employee_id,fiscalyear_id):
        periods=self.pool.get('account.period').search(self.cr, self.uid,[('fiscalyear_id','=',fiscalyear_id.id)])
        period_query_cond=str(tuple(periods))
        query = """
        SELECT sum(salaire_brute) AS salaire_brute, sum(salaire_brute_imposable) AS salaire_brute_imposable,
        sum(cotisations_employee) as cotisations_employee,sum(cotisations_employer) as cotisations_employer,
        sum(working_days) as working_days,sum(salaire_net) as salaire_net,sum(igr) as igr, sum(deduction) as deduction FROM hr_payroll_ma_bulletin WHERE period_id IN %s and employee_id = %s
         """%(str(period_query_cond),employee_id.id)
        self.cr.execute(query)
        data = self.cr.dictfetchall()
        return data
    
report_sxw.report_sxw('report.hr.payroll_ma.bulletin.2',
                      'hr.payroll_ma.bulletin',
                      'addons/syst_hr_payroll_ma/report/bulletin.rml',
                      parser=bulletin)
    
