#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
import netsvc
from osv import fields, osv
from mx import DateTime
from tools import config
from tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"

    def check_limit(self, cr, uid, ids, context={}):
        so = self.browse(cr, uid, ids[0], context)
        partner = so.partner_id
        non_cash_payment = (so.payment_term.name != 'Comptant')
        moveline_obj = self.pool.get('account.move.line')
	movelines = moveline_obj.search(cr, uid, [('account_id.reconcile','=',True),
						('partner_id', '=', partner.id),
						('account_id.type', 'in', ['receivable', 'payable']), 
						('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)
        maturity_reached=False
        debit, credit = 0.0, 0.0
	msg_ech=''
        for line in movelines:
	    if line.debit>0 and line.amount_residual_currency>0:
            	if line.date_maturity < time.strftime('%Y-%m-%d'):
			print line.debit,line.credit
			print credit-debit
                	credit += line.debit
                	debit += line.credit
            	if not line.reconcile_id and not maturity_reached:
                	print 'line reconcile is false'
                	if line.account_id.reconcile==True:
                    		#print 'account.reconcile is true'
                    		if not partner.x_maturity:
                        		if line.date_maturity <= time.strftime('%Y-%m-%d') and line.date_maturity>'1990-01-01' and line.debit>0:
                            			#print line.name
						#print 'residual',line.amount_residual_currency
                            			#print line.date_maturity
                            			#print 'debit',line.debit
                            			#print 'credit',line.credit
                            			#print 'ref',line.ref
						ln='Echu'+line.ref+','+line.name+','+str(line.debit)+','+str(line.credit)+','+str(line.amount_residual_currency)
						msg_ech+='\n'+ln
                            			maturity_reached=True
        
        if (credit - debit + so.amount_total) > partner.credit_limit or maturity_reached:
            if not partner.over_credit and non_cash_payment:
                msg = 'Confirmation Commande Impossible, Montant Total Due %s a la date de %s !\nVerifier le compte client ou la limite de credit!\n %s' % (credit - debit, time.strftime('%Y-%m-%d'),msg_ech)
                raise osv.except_osv(_('Depassement de limite de credit !'), _(msg))
                return False
            else:
                #self.pool.get('res.partner').write(cr, uid, [partner.id], {'credit_limit':credit - debit + so.amount_total})
                return True
        else:
            return True
    _columns = {
        'printed':fields.boolean('printed?'),       
    }    
sale_order()
