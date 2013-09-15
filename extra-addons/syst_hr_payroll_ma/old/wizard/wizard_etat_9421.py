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

import wizard
import datetime
import pooler
import time
import netsvc

form='''<?xml version="1.0"?>
<form string="Journal de Paie">
    <field name="fiscalyear_id"  colspan="2"/>
    <newline/>
    <field name="partner_id" select="1" colspan="2"/>
</form>'''
#<field name="employee_ids" colspan="2"/>
fields = {    
    'fiscalyear_id':{'string': 'Exercice fiscal', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True },
    'partner_id':{'string': 'Partenaire', 'type': 'many2one', 'relation': 'res.partner', 'required': True },
    #'employee_ids':{'string':'Employees', 'type':'many2many','relation':'hr.employee','required':True},
       }

class wizard_print(wizard.interface):
    def _get_defaults(self, cr, uid, data, context={}):
        data['form']={}
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
            'result':{'type':'print', 'report':'etat.9421', 'state':'end'}
        }
    }
wizard_print('wizard.etat.9421')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

