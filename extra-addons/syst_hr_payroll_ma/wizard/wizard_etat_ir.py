# -*- encoding: utf-8 -*-


import wizard
import datetime
import pooler
import time
import netsvc

form='''<?xml version="1.0"?>
<form string="Journal de Paie">
    <field name="fiscalyear_id" select="1" colspan="2"/>
    <newline/>
     <field name="period_id" select="1" colspan="2"/>
    <newline/>
    <field name="partner_id" select="1" colspan="2"/>
    <newline/>
</form>'''
#<field name="employee_ids" colspan="2"/>
fields = {    
    'fiscalyear_id':{'string': 'Exercice fiscal', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True },
    'period_id':{'string': 'Periode', 'type': 'many2one', 'relation': 'account.period', 'required': True },
    'partner_id':{'string': 'Partenaire', 'type': 'many2one', 'relation': 'res.partner', 'required': True },
    #'employee_ids':{'string':'Employees', 'type':'many2many','relation':'hr.employee','required':True},
       }

class wizard_etat_ir(wizard.interface):
    def _get_defaults(self, cr, uid, data, context={}):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear_id'] = fiscalyear_obj.find(cr, uid)
        company_obj = pooler.get_pool(cr.dbname).get('res.company')
        ids_company=company_obj.search(cr,uid,[])
        dictionnaire=company_obj.read(cr,uid,ids_company[0])
        data['form']['partner_id'] = dictionnaire['partner_id'][0]
        return data['form']

    states={
        'init':{
            'actions':[_get_defaults],
            'result':{'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel','gtk-cancel'),('report','Print','gtk-print')]}
        },
        'report':{
            'actions':[],
            'result':{'type':'print', 'report':'etat.ir', 'state':'end'}
        }
    }
wizard_etat_ir('wizard.etat.ir')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

