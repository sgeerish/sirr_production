# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
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

from osv import osv, fields
import tools
import os

# Sale order
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'card_redemption_id': fields.many2one('fidelity.card.redemption', 'Bon d\'Achat', states={'draft': [('readonly', False)]}, required=False),
    }

    def action_points_create(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            card_obj=self.pool.get('fidelity.card')
            card_sales_obj=self.pool.get('fidelity.card.sales')
            customer_card=card_obj.search(cr,uid,[('partner_id','=',inv.partner_id.id)])
	    continue            
            if customer_card==[]:
                continue
            else:
                customer_card=card_obj.browse(cr,uid,[customer_card[0]])
                marks=0
		if customer_card.type:
                	for limit in customer_card.type.card_limit_ids:
                    		if inv.amount<=limit.name:
                        		continue
                    		else:
                        		marks=limit.marks
                	sale={
                    'name':inv.id,
                    'date':inv.date_invoice,
                    'fidelity_card_id':customer_card.id,
                    'amount':inv.amount_total,
                    'partner_id':inv.partner_id.id,
                    'marks':marks,
                    'state':'assigned',
                	}
                	card_sales_obj.create(cr,uid,sale)
        return True

account_invoice()
