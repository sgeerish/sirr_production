# -*- encoding: utf-8 -*-
import time
import locale
import datetime
from report import report_sxw
import time
import pooler
import rml_parse
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

class journal_paie_report(rml_parse.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(journal_paie_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_period'  : self.get_period,
            'get_partner' : self.get_partner,
            'get_fiscalyear' : self.get_fiscalyear,
            'get_function' : self.get_function,
            'get_journal' : self.get_journal,
            'get_total' : self.get_total,
        })
    
        
    def get_fiscalyear(self,fiscalyear_id):
        fiscalyear_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        return fiscalyear_obj.read(self.cr,self.uid,[fiscalyear_id],['name'])[0]['name']
    
    def get_partner(self,partner_id):
        partner_obj = pooler.get_pool(self.cr.dbname).get('res.partner')
        return partner_obj.read(self.cr,self.uid,[partner_id],['name'])[0]['name']
    
    def get_period(self,period_id):
        period_obj = pooler.get_pool(self.cr.dbname).get('account.period')
        period=period_obj.read(self.cr,self.uid,[period_id])[0]
        return 'Periode du %s au %s'% (period['date_start'], period['date_stop'])
    
    def get_function(self,contract_id):
        contract = pooler.get_pool(self.cr.dbname).get('hr.contract')
        c=contract.read(self.cr,self.uid,[contract_id])[0]
        function = pooler.get_pool(self.cr.dbname).get('hr.job')
        f=function.read(self.cr,self.uid,[c['id']])[0]
        return f['name']
    
    def get_journal(self,period_id,partner_id):

        sql='''
        SELECT r.name,r.matricule,r.cin,r.date,e.birthday,b.salaire_net_a_payer,b.salaire_base,b.salaire_brute,
        b.salaire_brute_imposable,b.salaire_net,b.salaire_net_imposable,b.cotisations_employee,b.cotisations_employer,
        b.igr,b.prime,b.indemnite,b.avantage,b.exoneration,b.deduction,b.normal_hours,b.prime_anciennete,b.working_days,
        b.frais_pro,b.personnes,b.absence,b.employee_contract_id as contract
        FROM hr_payroll_ma_bulletin b
        LEFT JOIN hr_contract c on (b.employee_contract_id=c.id)
        LEFT JOIN hr_employee e on (b.employee_id=e.id)
        LEFT JOIN resource_resource r on (r.id=e.id)
        WHERE 
        (b.period_id=%s )  
        '''% (period_id)
        self.cr.execute(sql)
        journal=self.cr.dictfetchall()

        return journal
    
    def get_total(self,period_id):

        salaire_base=0
        salaire_brute=0
        salaire_brute_imposable=0
        salaire_net_a_payer=0
        salaire_net_imposable=0
        cotisations_employee=0
        cotisations_employer=0
        igr=0
        prime=0
        indemnite=0
        avantage=0
        exoneration=0
        deduction=0
        normal_hours=0
        prime_anciennete=0
        working_days=0
        frais_pro=0
        personnes=0
        absence=0
        tolal_line={}
        bulletins=self.pool.get('hr.payroll_ma.bulletin')
        bulletins_ids=bulletins.search(self.cr,self.uid,[('period_id','=',int(period_id))])
        liste=bulletins.read(self.cr,self.uid,bulletins_ids,[])
        for b in liste:
            salaire_base+=b['salaire_base']
            salaire_brute+=b['salaire_brute']
            salaire_brute_imposable+=b['salaire_brute_imposable']
            salaire_net_a_payer+=b['salaire_net_a_payer']
            salaire_net_imposable+=b['salaire_net_imposable']
            cotisations_employee+=b['cotisations_employee']
            cotisations_employer+=b['cotisations_employer']
            igr+=b['igr']
            prime+=b['prime']
            indemnite+=b['indemnite']
            avantage+=b['avantage']
            exoneration+=b['exoneration']
            deduction+=b['deduction']
            normal_hours+=b['normal_hours']
            prime_anciennete+=b['prime_anciennete']
            working_days+=b['working_days']
            frais_pro+=b['frais_pro']
            personnes+=b['personnes']
            absence+=b['absence']
            
        liste=[]
        print igr
        total_line={
            'salaire_base':salaire_base,
            'salaire_brute':salaire_brute,
            'salaire_brute_imposable':salaire_brute_imposable,
            'salaire_net_a_payer':salaire_net_a_payer,
            'salaire_net_imposable':salaire_net_imposable,
            'cotisations_employee':cotisations_employee,
            'cotisations_employer':cotisations_employer,
            'igr':igr,
            'prime':prime,
            'indemnite':indemnite,
            'avantage':avantage,
            'exoneration':exoneration,
            'deduction':deduction,
            'normal_hours':normal_hours,
            'prime_anciennete':prime_anciennete,
            'working_days':working_days,
            'frais_pro':frais_pro,
            'personnes':personnes,
            'absence':absence,
            }
        liste.append(total_line)
        return liste

report_sxw.report_sxw('report.journal.paie', 'hr.payroll_ma.bulletin', 'syst_hr_payroll_ma/report/journal_paie_report.rml', journal_paie_report)
       
       
               
