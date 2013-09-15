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
import convertion

class net_payer_report(rml_parse.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(net_payer_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_period'  : self.get_period,
            'get_city' : self.get_city,
            'get_net' : self.get_net,
            'get_total' : self.get_total,
            'get_bank' :self.get_bank,
            'total_text' : self.total_text 
        })
    
        
    def get_fiscalyear(self,fiscalyear_id):
        fiscalyear_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        return fiscalyear_obj.read(self.cr,self.uid,[fiscalyear_id],['name'])[0]['name']
    
    def get_city(self,partner_id):
        partner_obj = pooler.get_pool(self.cr.dbname).get('res.partner')
        partner=partner_obj.read(self.cr,self.uid,[partner_id],)[0]
        return partner['city']
    
    def get_period(self,period_id):
        period_obj = pooler.get_pool(self.cr.dbname).get('account.period')
        period=period_obj.read(self.cr,self.uid,[period_id])[0]
        return period['name']

    def get_bank(self,banque):
        _banque = pooler.get_pool(self.cr.dbname).get('res.bank')
        e=_banque.read(self.cr,self.uid,[banque])[0]
        bank={
            'name':e['name'],
            'street':e['street'],
            'code':e['code'],
            }
        return bank    
    
    def total_text(self,montant):
            devis = 'Dirham'      
            return convertion.trad(montant, devis)

    def get_function(self,contract_id):
        contract = pooler.get_pool(self.cr.dbname).get('hr.contract')
        c=contract.read(self.cr,self.uid,[contract_id])[0]
        function = pooler.get_pool(self.cr.dbname).get('hr.job')
        f=function.read(self.cr,self.uid,[c['id']])[0]
        return f['name']

    def get_net(self,period_id):

        sql='''
        SELECT r.name,r.compte,r.bank as bank,b.salaire_net_a_payer,b.employee_contract_id as contract
        FROM hr_payroll_ma_bulletin b
        LEFT JOIN hr_contract c on (b.employee_contract_id=c.id)
        LEFT JOIN resource_resource r on (b.employee_id=r.id)
        WHERE 
        (b.period_id=%s and r.mode_reglement='virement')
        '''% (period_id)
        self.cr.execute(sql)
        journal=self.cr.dictfetchall()

        return journal
    
    def get_total(self,period_id):
        salaire_net_a_payer=0
        #tolal_line={}
        #bulletins=self.pool.get('hr.payroll_ma.bulletin')
        #bulletins_ids=bulletins.search(self.cr,self.uid,[('period_id','=',int(period_id))])
        #liste=bulletins.read(self.cr,self.uid,bulletins_ids,[])
        for b in self.get_net(period_id):
            salaire_net_a_payer+=b['salaire_net_a_payer']
            
        return salaire_net_a_payer

report_sxw.report_sxw('report.net.payer', 'hr.payroll_ma.bulletin', 'syst_hr_payroll_ma/report/net_payer_report.rml', net_payer_report)
       
       
               
