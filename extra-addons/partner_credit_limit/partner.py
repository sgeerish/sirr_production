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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _get_over_limit(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        result = False
        partner_obj = self.pool.get('res.partner').browse(cr,uid,ids)
        print 'ids',ids
        partner=ids
        print 'partner', partner
        moveline_obj = self.pool.get('account.move.line')
        movelines = moveline_obj.search(cr, uid, [('account_id.reconcile','=',True),('partner_id', '=', partner),('account_id.type', 'in', ['receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)
        debit, credit = 0.0, 0.0            
        result=False
        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d'):
                credit += line.debit
                debit += line.credit
                
        if (credit - debit ) > partner_obj.credit_limit:
            result = True
        else:
            result = False
        return result
        
    def _get_over_due(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        result = False
        partner_obj = self.pool.get('res.partner').browse(cr,uid,ids)
        partner=ids
        moveline_obj = self.pool.get('account.move.line')
        movelines = moveline_obj.search(cr, uid, [('account_id.reconcile','=',True),('partner_id', '=', partner),('account_id.type', 'in', ['receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)
        debit, credit = 0.0, 0.0            
        result=False
        maturity_reached=False
        for line in movelines:
            if not line.reconcile_id and not maturity_reached:
                if line.account_id.reconcile==True:
                    if not partner_obj.x_maturity:
                        if line.date_maturity <= time.strftime('%Y-%m-%d') and line.date_maturity>'1990-01-01' and line.debit>0:
                            maturity_reached=True
                            
        if maturity_reached:
            result = True
        else:
            result= False
        return result 
            
    _columns = {
        'over_credit':fields.boolean('Allow Over Credit?', required=False),
        'over_limit':fields.boolean(string='Limite Atteint'),
        'over_due':fields.boolean(string='Echeance Atteint'),        
    }
    
    def update_customer_limits(self, cr, uid, ids=[], context={}):
        partner_obj = self.pool.get('res.partner')
        partners=partner_obj.search(cr,uid,[('ref','like','C%')])
        partners=partner_obj.browse(cr,uid,partners)
        for partner in partners:
            #print self._get_over_limit(cr,uid,partner)
            partner_obj.write(cr,uid,partner.id,{'x_overlimit':self._get_over_limit(cr,uid,partner.id),'x_overdue':self._get_over_due(cr,uid,partner.id),'over_credit':False,'x_maturity':False})
#            partner_obj.write(cr,uid,partner.id,{'x_overdue':self._get_over_due(cr,uid,partner.id)})
        return True
res_partner()

