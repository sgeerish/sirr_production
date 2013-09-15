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

situation_mfi_form = '''<?xml version="1.0"?>
<form string="Impayes Clients">
    <group col="8">
            <field name="date_to"/>
            <field name="location_id"/>
    </group>
</form>'''


situation_mfi_fields = {
        'date_to': {'string':'Aretee', 'type':'datetime'},
        'location_id': {'string':'Depot', 'type':'many2one','relation':'stock.location'},
    }


class wizard_situation_mfi(wizard.interface):

    def _get_defaults(self, cr, uid, data, context={}):       
        return data['form']
        
    def _get_states(self, cr, uid, data, context):
        return 'print_report_c'
            
    def _get_records(self, cr, uid, data, context={}):
        inv_obj = pooler.get_pool(cr.dbname).get('account.move.line')
        states = ['posted','valid']
        
        title = _("Impayes clients - ")
     
        ids = []
        moveline_obj = pooler.get_pool(cr.dbname).get('account.move.line')
#parametres
        comptes_clients=0
        valeur_stock=0
        portefeuille=0
        datas={}
#comptes clients
        movelines2 = moveline_obj.search(cr, uid,
            [#('partner_id', '=', partner.id),
                ('journal_id.type','in',['sale','sale_refund']),
                ('date','<=',DateTime.strptime(data['form']['date_to'][:10], '%Y-%m-%d')),
                ('state', 'not in', ['cancel','draft']), ('reconcile_id', '!=', False),
                ('account_id.type', 'in', ['receivable', 'payable']),
                ('state', '<>', 'draft'),('account_id.reconcile','=',True)]) 
                
        movelines2 = moveline_obj.browse(cr,uid,movelines2)
        lines=movelines2
        for y in lines:
            if not y.reconcile_id and not y.reconcile_partial_id:
                comptes_clients=comptes_clients+y.debit-y.credit
                ids.append(y.id)
            if y.reconcile_id:
                for rec_line in y.reconcile_id.line_id:
                    if rec_line.date<=data['form']['date_to'] and rec_line.state not in ('cancel','draft'):
                        comptes_clients=comptes_clients+y.debit-y.credit
            if y.reconcile_partial_id:
                for rec_line in y.reconcile_partial_id.line_id:
                    if rec_line.date<=data['form']['date_to'] and rec_line.state not in ('cancel','draft'):
                        comptes_clients=comptes_clients+y.debit-y.credit  
                        ids.append(y.id)
        ids=[]
        ids.append(y.id)                                
#valorisation stock
        product_obj = pooler.get_pool(cr.dbname).get('product.product')
        products=product_obj.search(cr,uid,[])
        products=product_obj.browse(cr,uid,products,context={'location':data['form']['location_id'],'to_date':data['form']['date_to']})
        for prod in products:
            if prod['virtual_available']>0:
                valeur_stock+=prod['virtual_available']*prod['standard_price']
#portefeuille
        voucher_obj = pooler.get_pool(cr.dbname).get('account.voucher')
        vouchers=voucher_obj.search(cr,uid,[('type','=','receipt'),('journal_id.x_portefeuille','=',True),('date','<=',DateTime.strptime(data['form']['date_to'][:10], '%Y-%m-%d'))])
        vouchers=voucher_obj.browse(cr,uid,vouchers)
        for voucher in vouchers:
            if voucher.reconciled:
                if voucher.banking_date<=DateTime.strptime(data['form']['date_to'][:10], '%Y-%m-%d'):
                    portefeuille+=voucher.amount
            else:
                portefeuille+=voucher.amount
            print 'portefeuille:',portefeuille
                
        title+=_(" Situation financiere")
        title+=_(" ")
        print 'stock : ',valeur_stock
        print 'comtpes : ',comptes_clients
        print 'portefeuille : ',portefeuille
        return {'ids' : ids , 
        'title' : title, 
        'detail':False ,
        'clients':comptes_clients,
        'stock':valeur_stock,
        'portefeuille':portefeuille} 
        
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {
                'type': 'form',
                'arch':situation_mfi_form,
                'fields':situation_mfi_fields,
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
                'report': 'report.situation_mfi',
                'rml' : 'ns_sales_reports/report/situation_mfi.jrxml',
                'state': 'end'
            },
        },
    }

wizard_situation_mfi('report.situation_mfi.wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
