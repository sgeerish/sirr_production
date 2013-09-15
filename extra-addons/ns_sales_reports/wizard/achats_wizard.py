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
from datetime import date
from mx import DateTime
from tools.translate import _

achats_form = '''<?xml version="1.0"?>
<form string="Impayes Clients">
    <group col="8">
        <group col="2">
        </group>
        <group col="2">
            <field name="code"/>
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
            <group colspan="4">
                <field name="invoice_date"/>
                <field name="maturity_date"/>
            </group>
            <field name="partner_id"/>
            <field name="detail"/>
        </group>
    </group>
</form>'''


achats_fields = {
        'period': {'string':'Period', 'type':'selection', 'selection':[('m','Month'),('a','Year'),('s','Selection')]},
        'month': {'string':'Month', 'type':'selection', 'selection':[('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]},
        'year': {'string':'Year', 'type':'selection', 'selection':[('2008','2008'),('2009','2009'),('2010','2010'),('2011','2001'),('2012','2012'),('2013','2013'),('2014','2014'),('2015','2015')]},
        'date_from': {'string':'From', 'type':'date'},
        'invoice_date': {'string':'Date de Facture <=', 'type':'date'},
        'maturity_date': {'string':'Date de Echeance <=', 'type':'date'},        
        'partner_id': {'string':'Client', 'type':'many2one','relation':'res.partner'},
        'detail':{'string':'Montrer Details?','type':'boolean'},
        'code':{'string':'Code Fournisseur','type':'char'},
    }


class wizard_achats(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
        print 'getting defaults'
        now=datetime.datetime.now()
        now= datetime.date(now.year, now.month, 1) - datetime.timedelta(days=1) # previous month
        data['form']['period'] = 's'
        data['form']['month'] = str(now.month)
        data['form']['year'] = str(now.year)
        return data['form']
        
    def _get_states(self, cr, uid, data, context):
        return 'print_report_c'
            
    def _get_records(self, cr, uid, data, context={}):
        inv_obj = pooler.get_pool(cr.dbname).get('account.invoice.line')
        ids = []
        states = ['posted','valid']
        
        title = _("Impayes clients - ")
     
        ids = []
        # print inv_ids
        partner_id=data['form']['partner_id']
        moveline_obj = pooler.get_pool(cr.dbname).get('account.invoice.line')
        #conditions de date
        if data['form']['invoice_date']=='':
            invoice_date= DateTime.strptime(data['form']['invoice_date'], '%Y-%m-%d') 
        else:
            invoice_date=date.today().strftime('%Y-%m-%d')
        print 'invoice_date',invoice_date

        if data['form']['maturity_date']=='':
            maturity_date= DateTime.strptime(data['form']['maturity_date'], '%Y-%m-%d') 
        else:
            maturity_date=date.today().strftime('%Y-%m-%d')
        print 'maturity date',maturity_date
        # print partners
        if data['form']['partner_id']:
            movelines = moveline_obj.search(cr, uid,
                [('partner_id', '=', partner_id),
                    ])
        elif data['form']['code']:
            partners=pooler.get_pool(cr.dbname).get('res.partner').search(cr,uid,[('ref','like','%'+data['form']['code']+'%')])
            movelines = moveline_obj.search(cr, uid,
                [('partner_id', 'in', partners),
                    ])
        else:
            movelines = moveline_obj.search(cr, uid,
                [#('partner_id', '=', partner.id),
                    ])
        
        movelines = moveline_obj.browse(cr, uid, movelines)
        
        if movelines:
            lines=movelines
            for x in lines:
                # for inv_line in x.move_line_id:
                    # print inv_line.product_id.name
                    # put other tests here if you want to filter lines
                ids.append(x.id)
        # print ids            
        title+=_(" ")
        if data['form']['detail']==0:
            detail=False
        else:
            detail=True
        
        return {'ids' : ids , 'title' : title, 'period' : data['form']['period'],
                'detail' : detail, 'year':data['form']['year']} 
        
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {
                'type': 'form',
                'arch':achats_form,
                'fields':achats_fields,
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
                'name' : 'Journal Caisse',
                'report': 'report.achats',
                'rml' : 'ns_sales_reports/report/achats.jrxml',
                'state': 'end'
            },
        },
    }

wizard_achats('report.achats.wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
