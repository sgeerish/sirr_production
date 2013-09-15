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

liste_factures_produits_form = '''<?xml version="1.0"?>
<form string="Revenue per product category">
    <group col="8">
        <group col="2">
        <field name="shop_id"/>
        </group>
        <group col="2">
            <field name="period" required="True"/>
            <newline/>
            <field name="draft"/>
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
            <newline/>
            <field name="hideproducts"/>
        </group>
    </group>
</form>'''

liste_factures_produits_fields = {
        'period': {'string':'Period', 'type':'selection', 'selection':[('m','Month'),('a','Year'),('s','Selection')]},
        'shop_id': {'string':'Souche', 'widget':'selection', 'type':'many2one', 'relation':'sale.shop'},
        'month': {'string':'Month', 'type':'selection', 'selection':[('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]},
        'year': {'string':'Year', 'type':'selection', 'selection':[('2008','2008'),('2009','2009'),('2010','2010'),('2011','2001'),('2012','2012'),('2013','2013'),('2014','2014'),('2015','2015')]},
        'date_from': {'string':'From', 'type':'date'},
        'date_to': {'string':'To', 'type':'date'},
        'draft': {'string':'Include draft invoices?', 'type':'boolean'},
        'hideproducts': {'string':'Show category summary only', 'type':'boolean'},
        'report': {'string':'Rapport', 'type':'selection', 
                'selection':[
                    ('c','per Category'),
                ]},
    }

class wizard_liste_factures_produits(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
        now=datetime.datetime.now()
        now= datetime.date(now.year, now.month, 1) - datetime.timedelta(days=1) # previous month
        data['form']['period'] = 'm'
        data['form']['month'] = str(now.month)
        data['form']['year'] = str(now.year)
        data['form']['draft'] = False
        data['form']['report'] = 'c'
        data['form']['hideproducts'] = False
        return data['form']
        
    def _get_states(self, cr, uid, data, context):
        return 'print_report_c'
            
    def _get_records(self, cr, uid, data, context={}):
    
        inv_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        shop_obj = pooler.get_pool(cr.dbname).get('sale.shop')
        ids = []
        if data['form']['draft']==True:
            states = ['draft','open','paid']
        else:
            states = ['open','paid']
        
        title = _("Statistiques Article - ")
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
        inv_ids = inv_obj.search(cr,uid,[
                  ('date_invoice','>=',day_min.strftime('%Y-%m-%d')),
                  ('date_invoice','<=',day_max.strftime('%Y-%m-%d')),
                  ('type','in',['out_invoice','out_refund','sale_refund']),
                  ('state','in',states),
               ])

        ids = []
        # print inv_ids
        shop_id=data['form']['shop_id']
        if shop_id:
            title += _(" - Souche ") +  shop_obj.browse(cr,uid,shop_id).name        
        if inv_ids:
            lines=inv_obj.browse(cr,uid,inv_ids)
            for x in lines:
                for inv_line in x.invoice_line:
                    # print inv_line.product_id.name
                    # put other tests here if you want to filter lines
                    if (inv_line.price_subtotal <> 0.0):
                        if shop_id:
                            if inv_line.invoice_id.user_id.shop.id==shop_id:
                                # if inv_line.price_subtotal==119675000:
                                    # print inv_line.id,inv_line.price_subtotal
                                ids.append(inv_line.id)                            
                        else:
                            ids.append(inv_line.id)

        return {'ids' : ids , 'title' : title, 'period' : data['form']['period'],
                'detail' : not data['form']['hideproducts'], 'year':data['form']['year']} 
        
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {
                'type': 'form',
                'arch':liste_factures_produits_form,
                'fields':liste_factures_produits_fields,
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
                'name' : 'Revenue per product',
                'report': 'ns_sales_reports.liste_factures_produits_c',
                'rml' : 'ns_sales_reports/report/liste_factures_produits_c.jrxml',
                'state': 'end'
            },
        },
    }

wizard_liste_factures_produits('jreports.ns_sales_products.wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
