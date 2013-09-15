# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2003-2010 NS-Team (<http://www.ns-team.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import pooler
import datetime
from mx import DateTime
from tools.translate import _

liste_factures_produits_com_form = '''<?xml version="1.0"?>
<form string="Revenue par Produit/Commercial">
    <group col="8">
        <group col="2">
        </group>
        <group col="2">
            <field name="period" required="True"/>
            <newline/>
            <field name="paid"/>
        </group>
        <group col="4">
            <group colspan="4"  attrs="{'invisible': [('period','=','s')]}">
                <group colspan="2">
                    <field name="year"/>
                </group>
                <group colspan="2" >
                    <field name="month" attrs="{'invisible': [('period','=','a')]}"/>
                </group>
            </group>
            <group colspan="4" attrs="{'invisible': [('period','in',('a','m'))]}">
                <field name="date_from"/>
                <field name="date_to"/>
            </group>
            <group>
                <field name="excluded_partner_id"  groups="account.group_account_manager"/>
                <field name="user_id"  groups="account.group_account_manager"/>
            </group>
            <group>
                <field name="comm_rate" groups="account.group_account_manager"/>
            </group>
            <newline/>
            <field name="hideproducts"/>
            <field name="all_users" groups="account.group_account_manager"/>            
        </group>
    </group>
</form>'''

liste_factures_produits_com_fields = {
        'period': {'string':'Periode', 'type':'selection', 'selection':[('m','Mois'),('a','Annee'),('s','Selection')]},
        'month': {'string':'Mois', 'type':'selection', 'selection':[('1','Janvier'),('2','Fevrier'),('3','Mars'),('4','Avril'),('5','May'),('6','Juin'),('7','Juillet'),('8','Aout'),('9','Septembre'),('10','Octobre'),('11','Novembre'),('12','Decembre')]},
        'year': {'string':'Annee', 'type':'selection', 'selection':[('2008','2008'),('2009','2009'),('2010','2010'),('2011','2001'),('2012','2012'),('2013','2013'),('2014','2014'),('2015','2015')]},
        'date_from': {'string':'De', 'type':'date'},
        'excluded_partner_id':{'string':'Clients a Exclure','type':'char'},
        'date_to': {'string':'A', 'type':'date'},
        'user_id':{'string':'Commercial','type':'char'},
        'comm_rate':{'string':'Taux','type':'float','digits':(12,6)},
        'draft': {'string':'Include draft invoices?', 'type':'boolean'},
        'hideproducts': {'string':'Show category summary only', 'type':'boolean'},
        'paid': {'string':'Factures Payes', 'type':'boolean'},     
        'all_users': {'string':'Tous les utilisateurs', 'type':'boolean'},                
        'report': {'string':'Rapport', 'type':'selection', 
                'selection':[
                    ('c','per Category'),
                ]},
    }

class wizard_liste_factures_produits_com(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
        now=datetime.datetime.now()
        now= datetime.date(now.year, now.month, 1) - datetime.timedelta(days=1) # previous month
        data['form']['period'] = 'm'
        data['form']['month'] = str(now.month)
        data['form']['year'] = str(now.year)
        data['form']['draft'] = False
        data['form']['report'] = 'c'
        data['form']['hideproducts'] = False
        data['form']['comm_rate'] = 0.0035
        data['form']['paid'] = False        
        data['form']['all_users'] = False                
        return data['form']
        
    def _get_states(self, cr, uid, data, context):
        return 'print_report_c'
            
    def _get_records(self, cr, uid, data, context={}):
        inv_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        ids = []
        if data['form']['draft']==True:
            states = ['draft','open','paid']
        else:
            states = ['open','paid']
        if data['form']['paid']==True:
            states = ['paid']
        
        title = _("Commissions - ")
        if data['form']['period'] == 'm':
            if int(data['form']['month']) < 10:
                title += "0"
            title += data['form']['month'] + "/" + data['form']['year']
            day_min = datetime.date(int(data['form']['year']), int(data['form']['month']), 1)
            nextmonth = int(data['form']['month']) + 1
            year = int(data['form']['year'])
            if nextmonth == 13:
                nextmonth = 1
                year += 1
            day_max = datetime.date(year, nextmonth, 1) - datetime.timedelta(days=1)
        elif data['form']['period'] == 's':
            day_min = DateTime.strptime(data['form']['date_from'], '%Y-%m-%d')        
            day_max = DateTime.strptime(data['form']['date_to'], '%Y-%m-%d')        
            title += _("De ") + day_min.strftime('%d/%m/%Y') + _(" A ") + day_max.strftime('%d/%m/%Y') 
        else:
            day_min = datetime.date(int(data['form']['year']), 1, 1)
            day_max = datetime.date(int(data['form']['year']), 12, 31)
            title += data['form']['year']
        if data['form']['user_id'] == False:
            user='%'
        else:
            user='%'+data['form']['user_id']+'%'
            
        if data['form']['all_users'] == False:
            user=''
            user='%'+pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['name'])['name']
            
        if data['form']['excluded_partner_id']==False:
            excl=[]
        else:
            excl=data['form']['excluded_partner_id'].split(',')
        partner_obj=pooler.get_pool(cr.dbname).get('res.partner')
        partner_ids=partner_obj.search(cr,uid,[('ref','in',excl)])
        if data['form']['paid']==True:
            inv_ids = inv_obj.search(cr,uid,[
                  ('date_invoice','>=','2012-05-31'),
                  ('x_exempt_comm','=',False),                  
                  ('type','in',['out_invoice','out_refund']),
                  ('state','in',states),
                  ('user_id','like',user),
                  ('partner_id','not in',partner_ids),
               ])
        else:
            inv_ids = inv_obj.search(cr,uid,[
                  ('date_invoice','>=',day_min.strftime('%Y-%m-%d')),
                  ('x_exempt_comm','=',False),                                    
                  ('date_invoice','<=',day_max.strftime('%Y-%m-%d')),
                  ('type','in',['out_invoice','out_refund']),
                  ('state','in',states),
                  ('user_id','like',user),
                  ('partner_id','not in',partner_ids),
               ])
        ids = []
        # print inv_ids
        if inv_ids:
            lines=inv_obj.browse(cr,uid,inv_ids)
            for x in lines:
                if data['form']['paid']==True: 
                    if x.payment_ids:
                        if x.payment_ids[0].date>=day_min.strftime('%Y-%m-%d'):
                            if x.payment_ids[0].date<=day_max.strftime('%Y-%m-%d'):
                                for inv_line in x.invoice_line:
                                    if (inv_line.price_subtotal <> 0.0):
                                        ids.append(inv_line.id)
                    # else:
                        # if x.type=='out_refund':
                            # if x.date_invoice>=day_min.strftime('%Y-%m-%d'):
                                # for inv_line in x.invoice_line:
                                        # if (inv_line.price_subtotal <> 0.0):
                                            # ids.append(inv_line.id)     
                else:
                        for inv_line in x.invoice_line:
                            if (inv_line.price_subtotal <> 0.0):
                                ids.append(inv_line.id)                
        title+=_(" ")
        if data['form']['paid']==True: 
            title+=_("Factures Payes : ")
        return {'ids' : ids , 'title' : title, 'period' : data['form']['period'],
                'detail' : not data['form']['hideproducts'], 'year':data['form']['year'],'comm_rate':data['form']['comm_rate'],'paid':data['form']['paid']} 
        
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {
                'type': 'form',
                'arch':liste_factures_produits_com_form,
                'fields':liste_factures_produits_com_fields,
                'state':[('end','Cancel'),('nextstate','Print')]
            },
        },
        'nextstate' : {
            'actions' : [],
            'result' : {'type' : 'choice', 'next_state' : _get_states}
        },
# This can be used to select various king of report presentation
#        'print_report_f': {
#            'actions': [_get_records],
#            'result': {
#                'type': 'print',
#                'name' : 'Revenue per product by ...',
#                'report': 'ns_sales_reports.liste_factures_produits_f',
#                'rml' : 'ns_sales_reports/report/liste_factures_produits_f.jrxml',
#                'state': 'end'
#            },
#        },
        'print_report_c': {
            'actions': [_get_records],
            'result': {
                'type': 'print',
                'name' : 'Revenue Produits Commercial',
                'report': 'ns_sales_reports.liste_factures_produits_c_com',
                'rml' : 'ns_sales_reports/report/liste_factures_produits_c_com.jrxml',
                'state': 'end'
            },
        },
    }

wizard_liste_factures_produits_com('jreports.ns_sales_products_com.wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
