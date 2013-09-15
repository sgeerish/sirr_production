# -*- encoding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import fields
from osv import osv
import time
from datetime import datetime, timedelta


class hotel_reservation(osv.osv):
    _name = "hotel.reservation"
    _description = "Reservation"
    _columns = {
        'reservation_no': fields.char('Reservation No', size=64, required=True,
                                      select=True),
        'date_order':fields.datetime('Date Ordered', required=True, readonly=True, 
                                     states={'draft':[('readonly',False)]}),
        'shop_id':fields.many2one('sale.shop', 'Shop', required=True, readonly=True, 
                                  states={'draft':[('readonly',False)]}),
        'partner_id':fields.many2one('res.partner', 'Guest Name', required=True,
                                     readonly=True, states={'draft':[('readonly',False)]}),
        'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True,
                                       readonly=True, states={'draft':[('readonly',False)]}),
        'partner_invoice_id':fields.many2one('res.partner.address', 'Invoice Address', 
                                             readonly=True, required=True, 
                                             states={'draft':[('readonly',False)]}),
        'partner_order_id':fields.many2one('res.partner.address', 'Ordering Contact',
                                           readonly=True, required=True, 
                                           states={'draft':[('readonly',False)]},
                                           help="The name and address of the contact that requested the order or quotation."),
        'partner_shipping_id':fields.many2one('res.partner.address', 'Shipping Address',
                                              readonly=True, required=True,
                                              states={'draft':[('readonly',False)]}),
        'checkin': fields.datetime('Expected Date Arrival',required=True,
                                   readonly=True, states={'draft':[('readonly',False)]}),
        'checkout': fields.datetime('Expected Date Departure',required=True,
                                    readonly=True, states={'draft':[('readonly',False)]}),
        'adults':fields.integer('Adults',size=64,readonly=True, 
                                states={'draft':[('readonly',False)]}),
        'childs':fields.integer('Children',size=64,readonly=True,
                                states={'draft':[('readonly',False)]}),
        'reservation_line':fields.one2many('hotel_reservation.line','line_id','Reservation Line'),
        'billing':fields.selection((('customer','Customer'),('agent','Agent')),'Billing'),
        'agent':fields.many2one('res.partner', 'Agent Name', readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft', 'Draft'),('confirm','Confirm'),
                                  ('cancel','Cancel'),('done','Done')], 'State',readonly=True),
        }

    _defaults = {
        'reservation_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'hotel.reservation'),
        'state': lambda *a: 'draft', 
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
       }

    def on_change_checkout(self,cr, uid, ids, checkin=time.strftime('%Y-%m-%d %H:%M:%S'),
                           checkout=time.strftime('%Y-%m-%d %H:%M:%S'),context=None):
        if checkout < checkin:
            raise osv.except_osv ('Error !','Checkout must be greater or equal checkin date')
        return {}

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'partner_invoice_id': False,
                    'partner_shipping_id':False,
                    'partner_order_id':False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery','invoice','contact'])
        pricelist = self.pool.get('res.partner').browse(cr, uid, part).property_product_pricelist.id
        return {'value':{
                'partner_invoice_id': addr['invoice'],
                'partner_order_id':addr['contact'],
                'partner_shipping_id':addr['delivery'],
                'pricelist_id': pricelist}}

    def confirmed_reservation(self,cr,uid,ids):
        for reservation in self.browse(cr, uid, ids):
            cr.execute("select count(*) from hotel_reservation as hr " \
                       "join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                       "where (hrl.checkin,hrl.checkout) overlaps ( timestamp %s , timestamp %s ) " \
                       "and hr.id <> cast(%s as integer) " \
                       "and hr.state = 'confirm' " \
                       "and hrl.product_id in ( " \
                       "select hrl.product_id from hotel_reservation_line as hrl " \
                       "join hotel_reservation hr on (hrl.line_id = hr.id) " \
                       "where hr.id = cast(%s as integer))"
                       ,(reservation.checkin,reservation.checkout,str(reservation.id),str(reservation.id))
                       )
            res = cr.fetchone()
            roomcount = res and res[0] or 0.0
            if roomcount:
                raise osv.except_osv('Warning', 'You tried to confirm reservation' \
                                     'with room those already reserved in this reservation period')
            else:
                self.write(cr, uid, ids, {'state':'confirm'})
            return True
    
    def _create_folio(self,cr,uid,ids):
        for reservation in self.browse(cr,uid,ids):
            product_oum_qty = (datetime(*time.strptime(reservation['checkout'],'%Y-%m-%d %H:%M:%S')[:5]) - 
                               datetime(*time.strptime(reservation['checkin'],'%Y-%m-%d %H:%M:%S')[:5])).days
            for line in reservation.reservation_line:
                print line.tax_id
                room_lines = {
                    'folio_id':line.id,
                    'checkin_date':line.checkin,
                    'checkout_date':line.checkout,
                    'product_id':line.product_id.id, 
                    'name':line.product_id.name,
                    'product_uom':line.product_id.uom_id.id,
                    'price_unit':line.price_unit,
                    'cost_price':line.cost_price,
					'tax_id':[(6, 0, [x.id for x in line.tax_id])],
                    'product_uom_qty': product_oum_qty,
                    'origin':line.product_id.id,
                }
                folio_data = {
                    'date_order':reservation.date_order,
                    'shop_id':reservation.shop_id.id,
                    'partner_id':reservation.partner_id.id,
                    'pricelist_id':reservation.pricelist_id.id,
                    'partner_invoice_id':reservation.partner_invoice_id.id,
                    'partner_order_id':reservation.partner_order_id.id,
                    'partner_shipping_id':reservation.partner_shipping_id.id,
                    'checkin_date': reservation.checkin,
                    'checkout_date': reservation.checkout,
                    'billing': reservation.billing,
                    'agent': reservation.agent.id,
                    'room_lines': [(0,0,room_lines)],
                    'room':line.product_id.id,
                    'adults':reservation.adults,
                    'childs':reservation.childs,
                    'origin':line.product_id.name,
                }
                folio=self.pool.get('hotel.folio').create(cr,uid, folio_data)
            self.write(cr, uid, ids, {'state':'done'})
        return True

hotel_reservation()

class hotel_reservation_line(osv.osv):
    _name = "hotel_reservation.line"
    #_rec_name = "product_id"
    _description = "Reservation Line"
    
    def _get_checkin(self,cr, uid, context={}):
       if 'checkin' in context:
           return context['checkin']
       return time.strftime('%Y-%m-%d %H:%M:%S')

    def _get_checkout(self,cr, uid, context={}):
       if 'checkin' in context:
           return context['checkout']
       return time.strftime('%Y-%m-%d %H:%M:%S')
       
    def _get_cur_partner_id(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        reservation=self.pool.get('hotel.reservation')
        for line in reservation.browse(cr, uid, ids):
            res[line.id]=line.partner_id.id
        return res

    _columns = {
        'name': fields.char('Reservation', size=64,select=True,required=True),
        'product_id':fields.many2one('product.product', 'Room',
                                     domain="[('isroom','=',True)]", required=True),
        'line_id':fields.many2one('hotel.reservation'),
        'categ_id': fields.many2one('product.category','Room Type',
                                    domain="[('isroomtype','=',True)]"),
        'price_unit': fields.float('Unit Price', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'cost_price': fields.float('Cost Price', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.related('line_id', 'state', type='selection', 
               selection=[('draft', 'Draft'),('confirm','Confirm'),('cancel','Cancel'),
               ('done','Done')], string='Reservation State', readonly=True),
        'checkin': fields.datetime('Expected Date Arrival', required=True),
        'checkout': fields.datetime('Expected Date Departure', required=True),
        'partner_id' : fields.related( 'line_id', 'partner_id', type="many2one", relation="res.partner", string="Guest", store=False),
        'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes', readonly=True, states={'draft': [('readonly', False)]})
     }

    _defaults={
       'checkin':_get_checkin,
       'checkout':_get_checkout,
       'name':'Reservation',
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
		        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
		        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,agent_id=False):
		    if not  partner_id:
		        raise osv.except_osv(_('No Customer Defined !'), _('You have to select a customer in the sales form !\nPlease set one customer before choosing a product.'))
		    if not  agent_id:
		        agent_id=1
		    warning = {}
		    product_uom_obj = self.pool.get('product.uom')
		    partner_obj = self.pool.get('res.partner')
		    product_obj = self.pool.get('product.product')
		    agent_pricelist=partner_obj.browse(cr, uid, agent_id).property_product_pricelist_purchase
		    agent_pricelist=agent_pricelist.id
		    if partner_id:
		        lang = partner_obj.browse(cr, uid, partner_id).lang
		    context = {'lang': lang, 'partner_id': partner_id}

		    if not product:
		        return {'value': {'th_weight': 0, 'product_packaging': False,
		            'product_uos_qty': qty}, 'domain': {'product_uom': [],
		               'product_uos': []}}
		    if not date_order:
		        date_order = time.strftime('%Y-%m-%d')

		    result = {}
		    product_obj = product_obj.browse(cr, uid, product, context=context)
		    if not packaging and product_obj.packaging:
		        packaging = product_obj.packaging[0].id
		        result['product_packaging'] = packaging

		    if packaging:
		        default_uom = product_obj.uom_id and product_obj.uom_id.id
		        pack = self.pool.get('product.packaging').browse(cr, uid, packaging, context=context)
		        q = product_uom_obj._compute_qty(cr, uid, uom, pack.qty, default_uom)
	#            qty = qty - qty % q + q
		        if qty and (q and not (qty % q) == 0):
		            ean = pack.ean or _('(n/a)')
		            qty_pack = pack.qty
		            type_ul = pack.ul
		            warn_msg = _("You selected a quantity of %d Units.\n"
		                        "But it's not compatible with the selected packaging.\n"
		                        "Here is a proposition of quantities according to the packaging:\n\n"
		                        "EAN: %s Quantity: %s Type of ul: %s") % \
		                            (qty, ean, qty_pack, type_ul.name)
		            warning = {
		                'title': _('Picking Information !'),
		                'message': warn_msg
		                }
		        result['product_uom_qty'] = qty

		    uom2 = False
		    if uom:
		        uom2 = product_uom_obj.browse(cr, uid, uom)
		        if product_obj.uom_id.category_id.id != uom2.category_id.id:
		            uom = False
		    if uos:
		        if product_obj.uos_id:
		            uos2 = product_uom_obj.browse(cr, uid, uos)
		            if product_obj.uos_id.category_id.id != uos2.category_id.id:
		                uos = False
		        else:
		            uos = False
		    if product_obj.description_sale:
		        result['notes'] = product_obj.description_sale
		    fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
		    if update_tax: #The quantity only have changed
		        result['delay'] = (product_obj.sale_delay or 0.0)
		        result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
		        result.update({'type': product_obj.procure_method})

		    if not flag:
		        result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context)[0][1]
		    domain = {}
		    if (not uom) and (not uos):
		        result['product_uom'] = product_obj.uom_id.id
		        if product_obj.uos_id:
		            result['product_uos'] = product_obj.uos_id.id
		            result['product_uos_qty'] = qty * product_obj.uos_coeff
		            uos_category_id = product_obj.uos_id.category_id.id
		        else:
		            result['product_uos'] = False
		            result['product_uos_qty'] = qty
		            uos_category_id = False
#		        result['th_weight'] = qty * product_obj.weight
		        domain = {'product_uom':
		                    [('category_id', '=', product_obj.uom_id.category_id.id)],
		                    'product_uos':
		                    [('category_id', '=', uos_category_id)]}

		    elif uos and not uom: # only happens if uom is False
		        result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
		        result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
		        result['th_weight'] = result['product_uom_qty'] * product_obj.weight
		    elif uom: # whether uos is set or not
		        default_uom = product_obj.uom_id and product_obj.uom_id.id
		        q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
		        if product_obj.uos_id:
		            result['product_uos'] = product_obj.uos_id.id
		            result['product_uos_qty'] = qty * product_obj.uos_coeff
		        else:
		            result['product_uos'] = False
		            result['product_uos_qty'] = qty
		        result['th_weight'] = q * product_obj.weight        # Round the quantity up

		    if not uom2:
		        uom2 = product_obj.uom_id
		    if (product_obj.type=='product') and (product_obj.virtual_available * uom2.factor < qty * product_obj.uom_id.factor) \
		      and (product_obj.procure_method=='make_to_stock'):
		        warning = {
		            'title': _('Not enough stock !'),
		            'message': _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. (without reservations)') %
		                (qty, uom2 and uom2.name or product_obj.uom_id.name,
		                 max(0,product_obj.virtual_available), product_obj.uom_id.name,
		                 max(0,product_obj.qty_available), product_obj.uom_id.name)
		        }
		    # get unit price
		    if not pricelist:
		        warning = {
		            'title': 'No Pricelist !',
		            'message':
		                'You have to select a pricelist or a customer in the sales form !\n'
		                'Please set one before choosing a product.'
		            }
		    else:
		        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
		                product, qty or 1.0, partner_id, {
		                    'uom': uom,
		                    'date': date_order,
		                    })[pricelist]
		        cost_price= self.pool.get('product.pricelist').price_get(cr, uid, [agent_pricelist],
		                product, qty or 1.0, agent_id, {
		                    'uom': uom,
		                    'date': date_order,
		                    })[agent_pricelist]
		        if price is False:
		            warning = {
		                'title': 'No valid pricelist line found !',
		                'message':
		                    "Couldn't find a pricelist line matching this product and quantity.\n"
		                    "You have to change either the product, the quantity or the pricelist."
		                }
		        else:
					print 'sex'
					result.update({'price_unit': price})
					result.update({'cost_price': cost_price})
					result.update({'categ_id':product_obj.categ_id.id})
		    return {'value': result, 'domain': domain, 'warning': warning}
       


    def on_change_checkout(self,cr, uid, ids, checkin=time.strftime('%Y-%m-%d %H:%M:%S'),
                           checkout=time.strftime('%Y-%m-%d %H:%M:%S'),context=None):
        if checkout < checkin:
            raise osv.except_osv ('Error !','Checkout must be greater or equal checkin date')
        return {}

    def on_change_product(self, cr, uid, ids, product_id, context=None):
        val = {'categ_id': None}
        if product_id:
            product_proxy = self.pool.get('product.product')
            for product in product_proxy.browse(cr, uid, [product_id], context=context):
                val['categ_id'] = product.categ_id.id
        return {'value': val}

hotel_reservation_line()

