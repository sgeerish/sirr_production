# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import pooler

class fleet_order(osv.osv):
    _name="fleet.order"
    _description="Fleet Orders"
    
    def ord_seq_get(self, cr, uid):
        pool_seq=self.pool.get('ir.sequence')
        cr.execute("select id,number_next,number_increment,prefix,suffix,padding from ir_sequence where code='fleet.order' and active=True")
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False
    
    def create(self, cr, user, vals, context=None):
        name=self.pool.get('ir.sequence').get(cr, user, 'fleet.order')
        return super(fleet_workorder,self).create(cr, user, vals, context)
    
    _rec_name="orderno"
    _columns={
              'orderno':fields.char('Order No',size=20,required=True),
              'orddate':fields.date('Order Date',required=True),
              'reqdate':fields.date('Book Date',required=True),
              'client_order_ref': fields.char('Customer Order Ref',size=64),
              'partner_id':fields.many2one('res.partner', 'Customer', readonly=True, states={'draft':[('readonly',False)]}, change_default=True, select=True),
              'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
              'partner_order_id':fields.many2one('res.partner.address', 'Ordering Contact', readonly=True, required=True, states={'draft':[('readonly',False)]}, help="The name and address of the contact that requested the order or quotation."),
              'partner_shipping_origin_id':fields.many2one('res.partner.address', 'Origin Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
              'partner_shipping_dest_id':fields.many2one('res.partner.address', 'Destination Address', readonly=True, required=True, states={'draft':[('readonly',False)]}),
              'state': fields.selection([
                ('draft','Enquired'),
                ('waiting_allotment','Waiting Allotment'),
                ('allotted','Vehicle Allotted'),
                ('progress','In Progress'),
                ('vehicle_except','Vehicle Exception'),
                ('invoice_except','Invoice Exception'),
                ('done','Done'),
                ('cancel','Cancel'),
                ('invoiced','Invoiced')
                ], 'Order State', readonly=True, help="Gives the state of the quotation or sale order. The exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the packing list process (Shipping Exception). The 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the date 'Date Ordered'.", select=True),
              'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft':[('readonly',False)]}),
              'payment_term' : fields.many2one('account.payment.term', 'Payment Term'),
              'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position'),
              'vehicle':fields.many2one('fleet.vehicle','Vehicle Allotted',required=True, states={'draft':[('readonly',False)],'waiting_allotment':[('readonly',False)]}),
              
              }
    _defaults={
            'orderno':lambda obj,cr,uid,context: obj.pool.get('fleet.order').wt_seq_get(cr,uid),
            'partner_invoice_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['invoice'])['invoice'],
            'partner_order_id': lambda self, cr, uid, context: context.get('partner_id', False) and  self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['contact'])['contact'],
            'partner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['delivery'])['delivery'],
            'partner_origin_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['origin'])['origin'],
            'partner_dest_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').address_get(cr, uid, [context['partner_id']], ['destination'])['destination'],
            'pricelist_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').browse(cr, uid, context['partner_id']).property_product_pricelist.id,
               }
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False, 'payment_term' : False, 'fiscal_position': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery','invoice','contact','origin','destination'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        return {'value':{'partner_invoice_id': addr['invoice'], 'partner_order_id':addr['contact'],'partner_shipping_origin_id':addr['origin'],'partner_shipping_dest_id':addr['destination'], 'partner_shipping_id':addr['delivery'], 'pricelist_id': pricelist, 'payment_term' : payment_term, 'fiscal_position': fiscal_position}}

