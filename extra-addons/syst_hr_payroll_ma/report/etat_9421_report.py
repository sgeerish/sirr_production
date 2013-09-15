# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2011 Systemum.com. All Rights Reserved
#    authors: Ahmed ELHAMIDI ah.elhamidi@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import locale
import datetime
from report import report_sxw
import time
import pooler
import rml_parse
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

class etat_9421_report(rml_parse.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(etat_9421_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_partner' : self.get_partner,
            'get_fiscalyear' : self.get_fiscalyear,
            'get_city' : self.get_city,
            'get_list' : self.get_list,
            'get_total' : self.get_total,
        })
    
        
    def get_fiscalyear(self,fiscalyear_id):
        fiscalyear_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        return fiscalyear_obj.read(self.cr,self.uid,[fiscalyear_id],['name'])[0]['name']
    
    def get_partner(self,partner_id):
        partner_obj = pooler.get_pool(self.cr.dbname).get('res.partner')
        return partner_obj.read(self.cr,self.uid,[partner_id],['name'])[0]['name']
    
    def get_city(self,partner_id):
        sql='''
        SELECT city
        FROM res_partner_address 
        WHERE 
        (partner_id = %s and type='default')
        '''% (partner_id)
        self.cr.execute(sql)
        list=self.cr.dictfetchone()
        return list['city']
    
    

        return f['name']
    def get_igr(self, montant, months, personnes):
        #print('fonction IGR')
        res = {}
        taux=0
        somme=0
        salaire_net_imposable = 0
        pool = pooler.get_pool(self.cr.dbname)
        params = self.pool.get('hr.payroll_ma.parametres')
        ids_params = params.search(self.cr, self.uid, [])
        dictionnaire = params.read(self.cr, self.uid, ids_params[0])
        
        salaire_net_imposable = montant 
        objet_ir = self.pool.get('hr.payroll_ma.ir')
        id_ir = objet_ir.search(self.cr, self.uid, [])
        liste = objet_ir.read(self.cr, self.uid, id_ir, ['debuttranche', 'fintranche', 'taux', 'somme'])
        for tranche in liste:
            if(salaire_net_imposable >= tranche['debuttranche']) and (salaire_net_imposable < tranche['fintranche']):
                taux = (tranche['taux'])
                somme = (tranche['somme']) 
            
        ir_brute = (salaire_net_imposable * taux / 100) - somme
        if((ir_brute - (personnes*months * dictionnaire['charge'])) < 0):
            ir_net = 0
        else:
            
            ir_net = ir_brute - (personnes*months * dictionnaire['charge'])
        res = {'ir_net':ir_net,
             }

        return res
    
    def get_list(self,fiscalyear_id):
        params = self.pool.get('hr.payroll_ma.parametres')
        ids_params = params.search(self.cr, self.uid, [])
        dictionnaire = params.read(self.cr, self.uid, ids_params[0])
        fraisPro = dictionnaire['fraispro']
        res=[]
        fiscalyear=self.pool.get('account.fiscalyear').browse(self.cr, self.uid, fiscalyear_id)
        periods=self.pool.get('account.period').search(self.cr, self.uid,[('fiscalyear_id','=',fiscalyear_id)])
        period_query_cond=str(tuple(periods))
        print period_query_cond
        sql='''
        SELECT r.name,r.matricule,r.cin,r.address_home,e.gender,e.children,r.chargefam,e.ssnid,sum(salaire_brute) as sb,
        sum(salaire_brute_imposable) as sbi,sum(salaire_net_imposable) as sni,sum(cotisations_employee) as ce,
        sum(avantage) as av,sum(exoneration) as ex,sum(working_days) as wd,sum(b.logement) as log,
        count(r.name) as nombre
        FROM hr_payroll_ma_bulletin b
        LEFT JOIN hr_employee e on (b.employee_id=e.id)
        LEFT JOIN hr_employee r on (r.id=e.id)
        WHERE 
        (b.period_id IN %s )
        group by r.name,r.matricule,r.cin,r.address_home,e.gender,e.children,r.chargefam,e.ssnid
        '''%(period_query_cond)
        print sql
        self.cr.execute(sql)
        list=self.cr.dictfetchall()
        for l in list:
            av=round(l['av'],2)
            si=round(l['sbi']-l['av'],2)
            sni=round(l['sni'],2)
            ce=round(l['ce'],2)
            log=round(l['log'],2)
            sb=round(l['sb'],2)
            ex=round(l['ex'],2)
            sbi=round(l['sbi'],2)
            dict={'name' : l['name'],'matricule' : l['matricule'],'cin':l['cin'],'address_home':l['address_home'],'cnss':l['ssnid'],
                    'children' : l['children'],'chargefam' :l['chargefam'],'sb':sb,'ex':ex,'sbi':sbi,
                    'av' : av,'si':si,'sni':sni,'fp':fraisPro,'ce':ce,'log':log,'wd':l['wd'],
                    'ir' : round(self.get_igr(l['sni'], l['nombre'], l['chargefam'])['ir_net'],2)
                      } 
            res.append(dict)
        return res
    
    def get_total(self,fiscalyear_id):

        sb=0
        ex=0
        sbi=0
        av=0
        si=0
        ce=0
        log=0
        sni=0
        ir=0
        
        tolal_line={}
        liste=self.get_list(fiscalyear_id)
        for l in liste:
            sb+=l['sb']
            ex+=l['ex']
            sbi+=l['sbi']
            av+=l['av']
            si+=l['si']
            ce+=l['ce']
            log+=l['log']
            sni+=l['sni']
            ir+=l['ir']
        liste=[]
        total_line={
            'sb':round(sb,2),
            'ex':round(ex,2),
            'sbi':round(sbi,2),
            'av':round(av,2),
            'si':round(si,2),
            'ce':round(ce,2),
            'log':round(log,2),
            'sni':round(sni,2),
            'ir':round(ir,2),
            }
        liste.append(total_line)
        return liste

report_sxw.report_sxw('report.etat.9421', 'hr.payroll_ma', 'syst_hr_payroll_ma/report/etat_9421_report.rml', etat_9421_report)
       
       
               
