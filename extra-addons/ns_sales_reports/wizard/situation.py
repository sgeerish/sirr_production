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

situation_form = '''<?xml version="1.0"?>
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
                <field name="invoice_date_debut"/>
                <field name="invoice_date_fin"/>
                
                <field name="ech"/>
            </group>
            <field name="partner_id"/>
            <field name="detail"/>
            <field name="paid"/>
        </group>
    </group>
</form>'''


situation_fields = {
        'date_to': {'string':'Arrete', 'type':'datetime'},
        'location_id': {'string':'Location', 'type':'many2one','relation':'stock.location'},
    }


class wizard_situation(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):
        now=datetime.datetime.now()
        now= datetime.date(now.year, now.month, 1) - datetime.timedelta(days=1) # previous month
        return data['form']
        
    def _get_states(self, cr, uid, data, context):
        return 'print_report_c'
            
    def _get_records(self, cr, uid, data, context={}):
        inv_obj = pooler.get_pool(cr.dbname).get('account.move.line')
        states = ['posted','valid']
        
        title = _("Impayes clients - ")
     
        ids = []
        moveline_obj = pooler.get_pool(cr.dbname).get('account.move.line')

        amount=0
        if (data['form']['paid'])!=0:
            paid=True
            movelines2 = moveline_obj.search(cr, uid,
                [#('partner_id', '=', partner.id),
                    ('journal_id.type','in',['sale','sale_refund']),
                    ('date','<=',data['form']['invoice_date_fin']),
                    ('date','>=',data['form']['invoice_date_debut']),
                    ('state', '<>', 'draft'), ('reconcile_id', '!=', False),
                    ('account_id.type', 'in', ['receivable', 'payable']),
                    ('state', '<>', 'draft'),('account_id.reconcile','=',True)]) 
                    
            movelines2 = moveline_obj.browse(cr,uid,movelines2)

            lines=movelines2
            for y in lines:
                if not y.reconcile_id and not y.reconcile_partial_id:
                    ids.append(x.id)
                if y.reconcile_id:
                    for rec_line in y.reconcile_id.line_id:
                        if rec_line.date<=data['form']['invoice_date_fin'] and rec_line.state not in ('cancel','draft'):
                            ids.append(rec_line.id)
                if y.reconcile_partial_id:
                    for rec_line in y.reconcile_partial_id.line_id:
                        if rec_line.date<=data['form']['invoice_date_fin'] and rec_line.state not in ('cancel','draft'):
                            ids.append(rec_line.id)                
                #if y.reconcile_id.line_id[0].date>=data['form']['invoice_date_fin']:
                #    amount=amount+y.debit-y.credit
                #    ids.append(y.id)
        else:
            paid=False
        movelines = moveline_obj.browse(cr, uid, movelines)
                
        print 'AMOUNT------------',amount
        title+=_(" ")
        if data['form']['detail']==0:
            detail=False
        else:
            detail=True
        if data['form']['paid']==0:
            paid=False
        else:
            paid=True
            
        return {'ids' : ids , 'title' : title, 'period' : data['form']['period'],
                'detail' : detail,'paid' : paid, 'year':data['form']['year']} 
        
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {
                'type': 'form',
                'arch':situation_form,
                'fields':situation_fields,
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
                'name' : 'Situation',
                'report': 'report.situation',
                'rml' : 'ns_sales_reports/report/situation.jrxml',
                'state': 'end'
            },
        },
    }

wizard_situation('report.situation.wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
