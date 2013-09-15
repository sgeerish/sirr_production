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
from osv import fields, osv
import datetime
from datetime import date
from mx import DateTime
import time

class small_expenses(osv.osv):
    _name="small.expenses"
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid)
        return periods and periods[0] or False
        
    _columns = {
        'date':fields.date('Date'),
        'partner_id':fields.many2one('res.partner','Fournisseur'),
        'payment_type_id':fields.many2one('account.voucher.type','Type de Depense'),
        'name':fields.char('Libele',size=64),
        'amount':fields.float('Montant'),
        'account_id':fields.many2one('account.account','Compte de Charge'),
        'creation':fields.many2one('res.users','Creation', readonly=True),
        'authorisation':fields.many2one('res.users','Autorisation',readonly=True),
        'validation':fields.many2one('res.users','Validation',readonly=True),        
        'move_id':fields.many2one('account.move','Piece Comptable',readonly=True),
        'journal_id':fields.many2one('account.journal','Journal'),
        'period_id':fields.many2one('account.period','Periode'),
	'beneficiary':fields.many2one('hr.employee','Beneficiaire'),        
        'state':fields.selection(
            [('draft','Brouillon'),
             ('open','En Cours'),
             ('valid','Valide'),
             ('auth','Autorise'),
             ('done','Termine')], 'State', readonly=True, size=32,)
    }
    _defaults = {
        'period_id': _get_period,
        'state':'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
    def validate(self,cr,uid,ids,*args):
        self.write(cr,uid,ids,{'validation':uid,'state':'valid'})
        return True

    def cancel(self,cr,uid,ids,*args):
        self.write(cr,uid,ids,{'state':'draft'})
        return True

        
    def authorise(self,cr,uid,ids,*args):
        self.write(cr,uid,ids,{'authorisation':uid,'state':'auth'})
        return True
        
    def pay(self,cr,uid,ids,*args):
        self.write(cr,uid,ids,{'state':'done'})
        if not ids: return []
        inv = self.browse(cr, uid, ids[0])
        view_obj=self.pool.get('ir.ui.view')
        view=view_obj.search(cr,uid,[('name','=','account.voucher.payment.form.depenses')])
        return {
            'name':'Decaissement',
            'view_mode': 'form',
            'view_id': view,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': str([('journal_id.type', '=','cash'),('type','=','payment')]),
            'context': {
                'default_partner_id': inv.partner_id.id,
                'default_amount': inv.amount,
                'default_name':inv.name,
                'close_after_process': True,
                'default_type': 'payment',
                'default_voucher_type_id':inv.payment_type_id.id,
                'type':'payment'
                }
        }
    
    def initiate(self,cr,uid,ids,*args):
        self.write(cr,uid,ids,{'creation':uid,'state':'open'})
        
small_expenses()

class cheque_return(osv.osv):
    _name="cheque.return"
    _columns = {
        'date':fields.date('Date'),
        'paiement':fields.many2one('account.voucher','Paiement'),
        'cheque':fields.char('No. cheque',size=30),
        'amount':fields.float('Montant'),
        'partner_id':fields.many2one('res.partner','Client')
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }    
cheque_return()

class customer_request(osv.osv):
    _name="customer.request"
    _columns={
        'date':fields.date('Date'),
        'name':fields.char('Nom/Raison Sociale',size=64),
        'add1':fields.char('Rue',size=64),
        'add2':fields.char('Rue 2',size=64),
        'ville':fields.char('Ville',size=64),
        'phone':fields.char('Telephone',size=64),
        'mobile':fields.char('Mobile',size=64),
        'country':fields.many2one('res.country','Pays'),
        'contact':fields.char('Nom de Contacte',size=64),
        'nif':fields.char('NIF',size=64),
        'stat':fields.char('STAT',size=64),
        'cif':fields.char('CIF',size=64),
        'rc':fields.char('RC',size=64),
        'email':fields.char('Email',size=64),
        'bank':fields.many2one('res.bank','Banque'),
        'account':fields.char('Numero de Compte',size=64),
        'credit_limit':fields.float('Plafond Demande'),
        'payment_term':fields.many2one('account.payment.term','Condition de Reglement'),
        'creation':fields.many2one('res.users','Demandeur'),
        'sc':fields.many2one('res.users','Service Commerciale'),
        'daf':fields.many2one('res.users','DAF'),
        'direction':fields.many2one('res.users','Direction'),
        'ref':fields.char('Code',size=32),
        'state':fields.selection([('draft','Brouillon'),
             ('open','Ouverte'),
             ('done','Termine')], 'State', readonly=True, size=32,)
    }
    _defaults={
        'creation':lambda obj, cr, uid, context: uid,
        'state':'draft',
    }
    
    def sc(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'sc': uid})
        
    def daf(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'daf': uid}) 
        
    def user(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'daf': uid,'state':'open'})
        
    def direction(self, cr, uid, ids, *args):
        partner_obj=self.pool.get('res.partner')
        partner_address_obj=self.pool.get('res.partner.address')
        self.write(cr, uid, ids, {'direction': uid,'state':'done'})
        for item in self.browse(cr,uid,ids):
            address=partner_address_obj.create(cr,uid,{
            'active':True,
            'city':item.ville,
            'country_id':item.country.id,
            'email':item.email,
            'street':item.add1,
            'street2':item.add2,
            'phone':item.phone,
            'mobile':item.mobile,
            'name':item.contact,
            'type':'default',
            }
            )
            val={
            'name':item.name,
            'ref':item.ref,
            'customer':True,
            'supplier':False,
            'address':[(6, 0, [address])],
            'x_rcs':item.rc,
            'x_nif':item.nif,
            'x_stat':item.stat,
            'x_cif':item.cif,
            }
            partner=partner_obj.create(cr,uid,val)
            partner_address_obj.write(cr,uid,address,{'partner_id':partner})
        view={
            'name':'Client',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': str([('name', '=', item.name)]),
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
	    'views':[(134,'tree'),(135,'form')]
        }
        return view
        
customer_request()

class res_partner(osv.osv):
    _inherit="res.partner"
    _description = " "
    _columns = {
        'cheque_ids':fields.one2many('cheque.return','partner_id',)
    }
res_partner()

class account_voucher(osv.osv):
    _inherit="account.voucher"
    _description = " "
    _columns = {
#       'transmission_id':fields.many2one('account.voucher.transmission','Versement'),
        'banking_id':fields.many2one('account.voucher.banking','Bordereau',)
    }
account_voucher()


class account_cheque_transmission(osv.osv):
	_name = "account.cheque.transmission"
	_description = "Transmission de cheque"
	_columns = {
		'name':fields.date('Date de versement'),
#		'voucher_ids':fields.one2many('account.voucher','transmission_id','Paiement'),
	        'state':fields.selection(
        	    [('draft','Brouillon'),
             		('expediate','Expedie'),
             		('banked','Mis En Banque')], 'State', readonly=True, size=32,),

	}

account_cheque_transmission()


class account_voucher_banking(osv.osv):
    _name="account.voucher.banking"
    _description = "Mise En Banque"
    _columns = {
        'name':fields.char('No bordereau', size=64),
        'cheque_ids':fields.one2many('account.voucher','banking_id','Effets'),
        'banking_date':fields.date('Mise En Banque'),
	'journal_id':fields.many2one('account.journal','Journal de banque'),
        'banking_bank':fields.many2one('res.bank','Banque'),
        'state':fields.selection(
            [('draft','Brouillon'),
             ('expediate','Expedie'),
             ('banked','Mis En Banque')], 'State', readonly=True, size=32,),
        
    }

#    def expediate(self.cr,uid,ids,context=None):
#        val={}
#	#val['banking_bank']=banking.banking_bank.id
        #val['banking_date']=banking.banking_date
        #val['banking_number']=banking.name
#    	self.write(cr,uid,ids,{'state':'expediate'})
#	for banking in self.browse(cr,uid,ids):
#		for voucher in banking.cheque_ids:
#			self.pool.get('account.voucher').write(cr,uid,voucher.id,val)
#	return True

#    def mis_en_banque(self.cr,uid,ids,context=None):
#        move_pool = self.pool.get('account.move')
#        move_line_pool = self.pool.get('account.move.line')
#        currency_pool = self.pool.get('res.currency')
#        tax_obj = self.pool.get('account.tax')
#        seq_obj = self.pool.get('ir.sequence')
	#for each voucher create a move and reconcile existing moveline for the voucher
#	for banking in self.browse(cr,uid,ids):
#		for voucher in banking.cheque_ids:
#			existing_move=False
#			for move in voucher.move_ids:
#				if move.account_id.id=voucher.journal_id.default_credit_account_id.id and move.debit>0:
#					existing_move=move
#			if banking.journal_id.sequence_id:
 #               		name = seq_obj.get_id(cr, uid, banking.journal_id.sequence_id.id)
  #          		else:
#                		raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))
#			move_id=move_pool.create(cr,uid,{
#					'name': name,
#		                	'journal_id': banking.journal_id.id,
#                			'narration': voucher.move_id.narration,
#                			'date': banking.date,
#                			'ref': voucher.move_id.ref,
##                			'period_id': voucher.move_id.period_id
#					})
#			move_line = {
#                		'name': name or '/',
#		                'debit': existing_move.credit,
#		                'credit': existing_move.debit,
#		                'account_id': existing_move.account_id.id,
#		                'move_id': move_id,
#		                'journal_id': banking.journal_id.id,
#		                'period_id': voucher.move_id.period_id.id,
#		                'partner_id': voucher.partner_id.id,
#		                'currency_id': company_currency <> current_currency and  current_currency or False,
#		                'amount_currency': company_currency <> current_currency and sign * voucher.amount or 0.0,
#		                'date': banking.date,
 #               		'date_maturity': banking.date
#            				}
#			move1=move_line_pool.create(cr, uid, move_line)
#			move_line = {
 #                               'name': name or '/',
  #                              'debit': existing_move.debit,
   #                             'credit': existing_move.credit,
#                                'account_id': banking.journal_id.default_credit_account_id.id,
#                                'move_id': move_id,
#                                'journal_id': banking.journal_id.id,
#                                'period_id': voucher.move_id.period_id.id,
#                                'partner_id': voucher.partner_id.id,
#                                'currency_id': company_currency <> current_currency and  current_currency or False,
#                                'amount_currency': company_currency <> current_currency and sign * voucher.amount or 0.0,
#                                'date': banking.date,
#                                'date_maturity': banking.date
#                                        }
#			move2=move_line_pool.create(cr, uid, move_line)
#			move_line_pool.reconcile_partial(cr, uid, [move1,existing_move.id])
#		self.write(cr,uid,banking.id,{'state':'banked'})
#		return true

    def validate(self,cr,uid,ids,context=None):
        voucher_obj=self.pool.get('account.voucher')
        move=self.pool.get('account.move.line')
        journal_obj=self.pool.get('account.journal')
        for banking in self.browse(cr,uid,ids):
            val={}
            val['banking_bank']=banking.banking_bank.id,
            val['banking_date']=banking.banking_date
            val['banking_number']=banking.name
            for voucher in banking.cheque_ids:
                journal=journal_obj.browse(cr,uid,voucher.journal_id.id)
                res={}
                for move_line in voucher.move_ids:
                    if journal.x_temporary_account and move_line.account_id==journal.default_credit_account_id:
                        print move_line.id  
                        print move_line.account_id
                        print journal.x_temporary_account.id
                        recs = []
                        recs += [move_line.id]
                        state=move_line.state
                        # move.write(cr,uid,recs,{'state':'draft'})
                        sql="UPDATE account_move_line set account_id=%d,bank=%d,x_banking_date='%s' where id=%d" % (journal.x_temporary_account.id,banking.banking_bank.id,banking.banking_date,move_line.id)
                        cr.execute(sql)
                        res2 = cr.commit()                    
                            # move.write(cr,uid,recs,{'account_id':journal.x_temporary_account.id,'state':state})
                
                voucher_obj.write(cr,uid,voucher.id,val) 
            self.write(cr,uid,ids,{'state':'expediate'})
            return True
            
    def banked(self,cr,uid,ids,context=None):
        voucher_obj=self.pool.get('account.voucher')
        move=self.pool.get('account.move.line')
        journal_obj=self.pool.get('account.journal')
        for banking in self.browse(cr,uid,ids):
            val={}
            val['x_recep_bank']=True,
            for voucher in banking.cheque_ids:
                voucher_obj.write(cr,uid,voucher.id,val) 
            return True
            
account_voucher_banking()

