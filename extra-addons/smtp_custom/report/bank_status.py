# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time

from report import report_sxw

class bank_status(report_sxw.rml_parse):
    _name = 'report.bank.status'

    def __init__(self, cr, uid, name, context):
        super(bank_status, self).__init__(cr, uid, name, context)    
        self.date=context['date']
        self.journal=context['journal_id']   
        self.banked=context['mis_en_banque']           
        self.localcontext.update({
            'date': self._get_date,
            'journal':self._get_journal,
            'banked':self._get_banked,
            'values':self._get_values,
            'products':self._get_products,
            
            
        })
        self.context = context

    def _get_date(self):
        return self.date
    def _get_journal(self):
        return self.journal
    def _get_banked(self):
        return self.banked 
    def _get_products(self):
        invoice_obj=self.pool.get('product.product')    
        ids=[]
        inv_ids=invoice_obj.search(self.cr,self.uid,[],context=self.context)        
        for prod in invoice_obj.browse(self.cr,self.uid,inv_ids,context=self.context):
            if prod.virtual_available>0:
                ids.append({'name':prod.name,'qty':prod.virtual_available, 'value':prod.standard_price,'sondage':prod.sondage})  
        return ids
        
    def _get_values(self):
        invoice_obj=self.pool.get('account.invoice')
        voucher_obj=self.pool.get('account.voucher')
        statement_obj=self.pool.get('account.bank.statement')
        vals=[]
        # get bank account
        statements=statement_obj.search(self.cr,self.uid,[('date','=',self.date),('journal_id.type','=','bank'),('journal_id.x_bank_id','!=',False),('x_net_value','!=',0)])
        statements=statement_obj.browse(self.cr,self.uid,statements)
        for statement in statements:
        #mis en banque
            traite=0
            traite_emises=[]
            cheque=0
            vouchers=voucher_obj.search(self.cr,self.uid,[('banking_date','=',self.date),('type','=','receipt'),('banking_bank','=',statement.journal_id.x_bank_id.id)])
            vouchers=voucher_obj.browse(self.cr,self.uid,vouchers)
            for voucher in vouchers:
                if voucher.journal_id.name[:6]=='Traite':
                    traite+=voucher.amount
                else:
                    cheque+=voucher.amount        #emises non credites
            vouchers=voucher_obj.search(self.cr,self.uid,[('date','<=',self.date),('banking_bank','=',statement.journal_id.x_bank_id.id),('type','=','payment'),('reconciled','=',False)])
            vouchers=voucher_obj.browse(self.cr,self.uid,vouchers)
            cheque_out=0
            traite_out=0
            for voucher in vouchers:
                if voucher.journal_id.name[:6]=='Traite':
                    traite_out+=voucher.amount
                    traite_emises.append(voucher)
                else:
                    cheque_out+=voucher.amount
            val={
            'banque':statement.journal_id.name,
            'net_value':statement.x_net_value,
            'virement':statement.x_provision-statement.x_paid,
            'traite_out':traite_out,
            'cheque_out':cheque_out,
            'traite':traite,
            'cheque':cheque,
            'autre_depot':statement.x_autre_depot,
            'autre_paiement':statement.x_autre_paiement,
            'date':self.date,
            'traite_emises':traite_emises,
            
            }
            vals.append(val)
        return vals
        
report_sxw.report_sxw('report.bank.status', 'account.account', 'addons/account/report/account_balance.rml', parser=bank_status)
report_sxw.report_sxw('report.product.product.location', 'product.product', 'addons/account/report/account_balance.rml', parser=bank_status)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
