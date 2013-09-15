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
import netsvc
import ir
from mx import DateTime
import datetime
import pooler
from tools import config

class hotel_floor(osv.osv):
    _name = "hotel.floor"
    _description = "Floor"
    _columns = { 
        'name': fields.char('Floor Name', size=64, required=True,select=True),
        'sequence' : fields.integer('Sequence', size=64),
        }    
hotel_floor()

class product_category(osv.osv):
    _inherit="product.category"
    _columns = {
        'isroomtype':fields.boolean('Is Room Type'),
        'isamenitype':fields.boolean('Is amenities Type'),
        'isservicetype':fields.boolean('Is Service Type'),
    }
product_category()

class hotel_room_type(osv.osv):
    _name = "hotel.room_type"
    _inherits = {'product.category':'cat_id'}
    _description = "Room Type"
    _columns = { 
        'cat_id':fields.many2one('product.category','category',required=True,select=True),
   
    }
    _defaults = {
        'isroomtype': lambda *a: 1,
    }    
hotel_room_type()


class product_product(osv.osv):
    _inherit="product.product"
    _columns = {
        'isroom':fields.boolean('Is Room'),
        'iscategid':fields.boolean('Is categ id'),
        'isservice':fields.boolean('Is Service id'),
                
    }
product_product()

class hotel_room_amenities_type(osv.osv):
    _name='hotel.room_amenities_type'
    _description='amenities Type'
    _inherits = {'product.category':'cat_id'}
    _columns = {
        'cat_id':fields.many2one('product.category','category',required=True),
       }
    _defaults = {
        'isamenitype': lambda *a: 1,
        
    }

hotel_room_amenities_type()

class hotel_room_amenities(osv.osv):
    _name='hotel.room_amenities'
    _description='Room amenities'
    _inherits={'product.product':'room_categ_id'}
    _columns = {
               
         'room_categ_id':fields.many2one('product.product','Product Category',required=True),
         'rcateg_id':fields.many2one('hotel.room_amenities_type','Amenity Catagory'),   
         'amenity_rate':fields.integer('Amenity Rate'),


        }
    _defaults = {
        'iscategid': lambda *a: 1,
        }
        
hotel_room_amenities()

class hotel_room(osv.osv):
  
    _name='hotel.room'
    _inherits={'product.product':'product_id'}
    _description='Hotel Room'
    _columns = {

        'product_id': fields.many2one('product.product','Product_id'),
        'floor_id':fields.many2one('hotel.floor','Floor No'),
        'max_adult':fields.integer('Max Adult'),
        'max_child':fields.integer('Max Child'),
        'avail_status':fields.selection([('assigned','Assigned'),(' unassigned','Unassigned')],'Room Status'),
        'room_amenities':fields.many2many('hotel.room_amenities','temp_tab','room_amenities','rcateg_id','Room Amenities'),
        }
    _defaults = {
        'isroom': lambda *a: 1,
        'rental': lambda *a: 1,
        }

hotel_room()

class hotel_folio(osv.osv):
    
    def _incoterm_get(self, cr, uid, context={}):
        return  self.pool.get('sale.order')._incoterm_get(cr, uid, context={})
    def copy(self, cr, uid, id, default=None,context={}):
        return  self.pool.get('sale.order').copy(cr, uid, id, default=None,context={})
    def _invoiced(self, cursor, user, ids, name, arg, context=None):
        return  self.pool.get('sale.order')._invoiced(cursor, user, ids, name, arg, context=None)
    def _invoiced_search(self, cursor, user, obj, name, args):
        return  self.pool.get('sale.order')._invoiced_search(cursor, user, obj, name, args)
    def _amount_untaxed(self, cr, uid, ids, field_name, arg, context):
        return self.pool.get('sale.order')._amount_untaxed(cr, uid, ids, field_name, arg, context)
    def _amount_tax(self, cr, uid, ids, field_name, arg, context):
        return self.pool.get('sale.order')._amount_tax(cr, uid, ids, field_name, arg, context)
    def _amount_total(self, cr, uid, ids, field_name, arg, context):
        return self.pool.get('sale.order')._amount_total(cr, uid, ids, field_name, arg, context)
        
    _name='hotel.folio'
    _description='hotel folio new'
    _inherits={'sale.order':'order_id'}
    #_inherit=   'sale.order'
    _columns={
          'order_id':fields.many2one('sale.order','order_id',required=True,ondelete='cascade'),
          'checkin_date': fields.datetime('Check In',required=True,readonly=True, states={'draft':[('readonly',False)]}),
          'checkout_date': fields.datetime('Check Out',required=True,readonly=True, states={'draft':[('readonly',False)]}),
          'room_lines': fields.one2many('hotel_folio.line','folio_id'),
          'service_lines': fields.one2many('hotel_service.line','folio_id'),
          'billing':fields.selection((('customer','Customer'),('agent','Agent')),'Billing'),
          'agent':fields.many2one('res.partner', 'Agent Name', readonly=True, states={'draft':[('readonly',False)]}),
          'room':fields.many2one('product.product', 'Room',
                                     domain="[('isroom','=',True)]"),
          'adults':fields.integer('Adults',size=64,readonly=True, 
                                states={'draft':[('readonly',False)]}),
          'childs':fields.integer('Children',size=64,readonly=True,
                                states={'draft':[('readonly',False)]}),
        

    }
    
    def manual_invoice(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        inv_ids = set()
        inv_ids1 = set()
        for id in ids:
            for record in self.pool.get('hotel.folio').browse(cr, uid, id).invoice_ids:
                inv_ids.add(record.id)
        # inv_ids would have old invoices if any
        for id in ids:
            wf_service.trg_validate(uid, 'hotel.folio', id, 'manual_invoice', cr)
            for record in self.pool.get('hotel.folio').browse(cr, uid, id).invoice_ids:
                inv_ids1.add(record.id)
        inv_ids = list(inv_ids1.difference(inv_ids))

        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,

        return {
            'name': 'Customer Invoices',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_ids and inv_ids[0] or False,
        }
    
    def create(self, cr, uid, vals, context=None, check=True):
        tmp_room_lines = vals.get('room_lines',[])
        tmp_service_lines = vals.get('service_lines',[])
        if not vals.has_key("folio_id"):
            vals.update({'room_lines':[],'service_lines':[]})
            folio_id = super(hotel_folio, self).create(cr, uid, vals, context)
            for line in tmp_room_lines:
                line[2].update({'folio_id':folio_id})
            for line in tmp_service_lines:
                line[2].update({'folio_id':folio_id})
            vals.update({'room_lines':tmp_room_lines,'service_lines':tmp_service_lines})
            super(hotel_folio, self).write(cr, uid,[folio_id], vals, context)
        else:
            folio_id = super(hotel_folio, self).create(cr, uid, vals, context)
        return folio_id
    
   
    def onchange_shop_id(self, cr, uid, ids, shop_id):
        return  self.pool.get('sale.order').onchange_shop_id(cr, uid, ids, shop_id)
    
    def onchange_partner_id(self, cr, uid, ids, part):
        return  self.pool.get('sale.order').onchange_partner_id(cr, uid, ids, part)
    
    def button_dummy(self, cr, uid, ids, context={}):
        return  self.pool.get('sale.order').button_dummy(cr, uid, ids, context={})
        
    def inv_line_create(self, cr, uid, a, ol):
        return (0, False, {
            'name': ol.name,
            'account_id': a,
            'price_unit': ol.cost_price or 0.0,
            'quantity': ol.product_uom_qty,
            'product_id': ol.product_id.id or False,
            'uos_id': ol.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in ol.tax_id])],
        })
    def action_invoice_create2(self, cr, uid, ids, *args):
        res = False
        journal_obj = self.pool.get('account.journal')
        sale_obj = self.pool.get('sale.order')
        journal_obj = self.pool.get('account.journal')
        for o in self.browse(cr, uid, ids):
            il = []
            todo = []
            for ol in o.order_line:
                todo.append(ol.id)
                if ol.product_id:
                    a = ol.product_id.product_tmpl_id.property_account_expense.id
                    if not a:
                        a = ol.product_id.categ_id.property_account_expense_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'), _('There is no expense account defined for this product: "%s" (id:%d)') % (ol.product_id.name, ol.product_id.id,))
                else:
                    a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category').id
                fpos = o.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                il.append(self.inv_line_create(cr, uid, a, ol))

            a = o.partner_id.property_account_payable.id
            journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),('company_id', '=', o.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error !'),
                    _('There is no purchase journal defined for this company: "%s" (id:%d)') % (o.company_id.name, o.company_id.id))
            room=o.origin
            checkin=o.checkin_date
            checkout=o.checkout_date
            reference='Room [%s]-IN [%s]-OUT [%s]'%(room,checkin,checkout)
            inv = {
                'name': o.name,
                'reference': reference,
                'account_id': a,
                'type': 'in_invoice',
                'partner_id': o.agent.id,
                'currency_id': o.pricelist_id.currency_id.id,
                'address_invoice_id': o.agent.address[0].id,
                'address_contact_id': o.agent.address[0].id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'origin': o.name,
                'invoice_line': il,
                'fiscal_position': o.fiscal_position.id or o.partner_id.property_account_position.id,
                'payment_term': o.partner_id.property_payment_term and o.partner_id.property_payment_term.id or False,
                'company_id': o.company_id.id,
            }
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv, {'type':'in_invoice'})
            self.pool.get('account.invoice').button_compute(cr, uid, [inv_id], {'type':'in_invoice'}, set_total=True)
            self.write(cr, uid, [o.id], {'invoice_ids': [(4, inv_id)]})
            res = inv_id
        return res
    def _inv_get(self, cr, uid, order, context=None):
        return {}
    def _make_invoice(self, cr, uid, order, lines, context=None):
        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}

        journal_ids = journal_obj.search(cr, uid, [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)], limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error !'),
                _('There is no sales journal defined for this company: "%s" (id:%d)') % (order.company_id.name, order.company_id.id))
        a = order.partner_id.property_account_receivable.id
        pay_term = order.payment_term and order.payment_term.id or False
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                    lines.append(inv_line_id)
        room=order.origin
        checkin=order.checkin_date
        checkout=order.checkout_date
        reference='Room [%s]-IN [%s]-OUT [%s]'%(room,checkin,checkout)
        inv = {
            'name': order.client_order_ref or '',
            'origin': order.origin,
            'type': 'out_invoice',
            'reference': reference,
            'account_id': a,
            'partner_id': order.agent.id,
            'journal_id': journal_ids[0],
            'address_invoice_id': order.agent.address[0].id,
            'address_contact_id': order.agent.address[0].id,
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.partner_id.name,
            'payment_term': pay_term,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice',False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'price_type':'tax_included'
        }
        inv.update(self._inv_get(cr, uid, order))
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], pay_term, time.strftime('%Y-%m-%d'))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id
            
    def action_invoice_create3(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_inv = False, context=None):
        res = False
        invoices = {}
        invoice_ids = []
        picking_obj = self.pool.get('stock.picking')
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        if context is None:
            context = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_inv:
            context['date_inv'] = date_inv
        for o in self.browse(cr, uid, ids, context=context):
            lines = []
            for line in o.order_line:
                if line.invoiced:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.agent.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                invoice_ref = ''
                for o, l in val:
                    invoice_ref += o.name + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    if o.order_policy == 'picking':
                        picking_obj.write(cr, uid, map(lambda x: x.id, o.picking_ids), {'invoice_state': 'invoiced'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                invoice.write(cr, uid, [res], {'origin': invoice_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(cr, uid, order, il, context=context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    if order.order_policy == 'picking':
                        picking_obj.write(cr, uid, map(lambda x: x.id, order.picking_ids), {'invoice_state': 'invoiced'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
        return res

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed','done','manual']):
        agent=False
        for o in self.browse(cr, uid, ids):
            agent=o.agent
            billing=o.billing

        if agent:
            print 'Enterred Agent'
            if billing=='customer':
				i = self.pool.get('sale.order').action_invoice_create(cr, uid, ids, grouped=False, states=['confirmed','done'])
				i = self.action_invoice_create2(cr, uid, ids)   
            else:
                i = self.action_invoice_create3(cr, uid, ids)
        else:    
            i = self.pool.get('sale.order').action_invoice_create(cr, uid, ids, grouped=False, states=['confirmed','done'])

        return i 
   
    def action_invoice_cancel(self, cr, uid, ids, context={}):
        res = self.pool.get('sale.order').action_invoice_cancel(cr, uid, ids, context={})
        for sale in self.browse(cr, uid, ids):
            for line in sale.order_line:
                self.pool.get('sale.order.line').write(cr, uid, [line.id], {'invoiced': False})
        #self.write(cr, uid, ids, {'state':'invoice_except', 'invoice_id':False})
        self.write(cr, uid, ids, {'state':'invoice_except'})
        return res  
    def action_cancel(self, cr, uid, ids, context={}):
        c = self.pool.get('sale.order').action_cancel(cr, uid, ids, context={})
        ok = True
        for sale in self.browse(cr, uid, ids):
            for r in self.read(cr,uid,ids,['picking_ids']):
                for pick in r['picking_ids']:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', pick, 'button_cancel', cr)
            for r in self.read(cr,uid,ids,['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
            
        self.write(cr,uid,ids,{'state':'cancel'})
        return c
    
    def action_wait(self, cr, uid, ids, *args):
        res = self.pool.get('sale.order').action_wait(cr, uid, ids, *args)
        for o in self.browse(cr, uid, ids):
            if (o.order_policy == 'manual') and (not o.invoice_ids):
                self.write(cr, uid, [o.id], {'state': 'manual'})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress'})
        print res
        return res
    def test_state(self, cr, uid, ids, mode, *args):
        write_done_ids = []
        write_cancel_ids = []
        res = self.pool.get('sale.order').test_state(cr, uid, ids, mode, *args)
        if write_done_ids:
            self.pool.get('sale.order.line').write(cr, uid, write_done_ids, {'state': 'done'})
        if write_cancel_ids:
            self.pool.get('sale.order.line').write(cr, uid, write_cancel_ids, {'state': 'cancel'})
        return res 
    def procurement_lines_get(self, cr, uid, ids, *args):
        res = self.pool.get('sale.order').procurement_lines_get(cr, uid, ids, *args)
        return  res
    def action_ship_create(self, cr, uid, ids, *args):
        res =  self.pool.get('sale.order').action_ship_create(cr, uid, ids, *args)
        return res
    def action_ship_end(self, cr, uid, ids, context={}):
        res = self.pool.get('sale.order').action_ship_end(cr, uid, ids, context={})
        for order in self.browse(cr, uid, ids):
            val = {'shipped':True}
            self.write(cr, uid, [order.id], val)
        return res 
    def _log_event(self, cr, uid, ids, factor=0.7, name='Open Order'):
        return  self.pool.get('sale.order')._log_event(cr, uid, ids, factor=0.7, name='Open Order')
    def has_stockable_products(self,cr, uid, ids, *args):
        return  self.pool.get('sale.order').has_stockable_products(cr, uid, ids, *args)
    def action_cancel_draft(self, cr, uid, ids, *args):
        d = self.pool.get('sale.order').action_cancel_draft(cr, uid, ids, *args)
        self.write(cr, uid, ids, {'state':'draft', 'invoice_ids':[], 'shipped':0})
        self.pool.get('sale.order.line').write(cr, uid,ids, {'invoiced':False, 'state':'draft', 'invoice_lines':[(6,0,[])]})
        return d
  
hotel_folio()

class hotel_folio_line(osv.osv):
    
    def copy(self, cr, uid, id, default=None, context={}):
        return  self.pool.get('sale.order.line').copy(cr, uid, id, default=None, context={})
    def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
        return  self.pool.get('sale.order.line')._amount_line_net(cr, uid, ids, field_name, arg, context)
    def _amount_line(self, cr, uid, ids, field_name, arg, context):
        return  self.pool.get('sale.order.line')._amount_line(cr, uid, ids, field_name, arg, context)
    def _number_packages(self, cr, uid, ids, field_name, arg, context):
        return  self.pool.get('sale.order.line')._number_packages(cr, uid, ids, field_name, arg, context)
    def _get_1st_packaging(self, cr, uid, context={}):
        return  self.pool.get('sale.order.line')._get_1st_packaging(cr, uid, context={})
    def _get_checkin_date(self,cr, uid, context={}):
        if 'checkin_date' in context:
            return context['checkin_date']
        return time.strftime('%Y-%m-%d %H:%M:%S')
    def _get_checkout_date(self,cr, uid, context={}):
        if 'checkin_date' in context:
            return context['checkout_date']
        return time.strftime('%Y-%m-%d %H:%M:%S')
 
    _name='hotel_folio.line'
    _description='hotel folio1 room line'
    _inherits={'sale.order.line':'order_line_id'}
    _columns={
          'order_line_id':fields.many2one('sale.order.line','order_line_id',required=True,ondelete='cascade'),
          'folio_id':fields.many2one('hotel.folio','folio_id',ondelete='cascade'),
          'checkin_date': fields.datetime('Check In',required=True),
          'checkout_date': fields.datetime('Check Out',required=True),
          'cost_price': fields.float('Cost Price', readonly=True, states={'draft': [('readonly', False)]}),
    }
    _defaults={
       'checkin_date':_get_checkin_date,
       'checkout_date':_get_checkout_date,
       
    }

    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        if vals.has_key("folio_id"):
            folio = self.pool.get("hotel.folio").browse(cr,uid,[vals['folio_id']])[0]
            vals.update({'order_id':folio.order_id.id})
        roomline = super(osv.osv, self).create(cr, uid, vals, context)
        return roomline
    
    def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
        return  self.pool.get('sale.order.line').uos_change(cr, uid, ids, product_uos, product_uos_qty=0, product_id=None)
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        return  self.pool.get('sale.order.line').product_id_change(cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='',partner_id=partner_id,
            lang=False, update_tax=True, date_order=False)
        
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        return  self.pool.get('sale.order.line').product_uom_change(cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=partner_id,
            lang=False, update_tax=True, date_order=False)
        
    def on_change_checkout(self,cr, uid, ids, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'),checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'),context=None):
        qty = 1
        if checkout_date < checkin_date:
            raise osv.except_osv ('Error !','Checkout must be greater or equal checkin date')
        if checkin_date:
            diffDate = datetime.datetime(*time.strptime(checkout_date,'%Y-%m-%d %H:%M:%S')[:5]) - datetime.datetime(*time.strptime(checkin_date,'%Y-%m-%d %H:%M:%S')[:5])
            qty = diffDate.days
            if qty == 0:
                qty=1
        return {'value':{'product_uom_qty':qty}}
    
    def button_confirm(self, cr, uid, ids, context={}):
        return  self.pool.get('sale.order.line').button_confirm(cr, uid, ids, context={})

    def button_done(self, cr, uid, ids, context={}):
        res = self.pool.get('sale.order.line').button_done(cr, uid, ids, context={})
        wf_service = netsvc.LocalService("workflow")
        res = self.write(cr, uid, ids, {'state':'done'})
        for line in self.browse(cr,uid,ids,context):
            wf_service.trg_write(uid, 'sale.order', line.order_id.id, cr)
        return res

        
    def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
        return  self.pool.get('sale.order.line').uos_change(cr, uid, ids, product_uos, product_uos_qty=0, product_id=None)
    def copy(self, cr, uid, id, default=None,context={}):
        return  self.pool.get('sale.order.line').copy(cr, uid, id, default=None,context={})
    
        

hotel_folio_line()

class hotel_service_line(osv.osv):
    
    def copy(self, cr, uid, id, default=None, context={}):
        return  self.pool.get('sale.order.line').copy(cr, uid, id, default=None, context={})
    def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
        return  self.pool.get('sale.order.line')._amount_line_net(cr, uid, ids, field_name, arg, context)
    def _amount_line(self, cr, uid, ids, field_name, arg, context):
        return  self.pool.get('sale.order.line')._amount_line(cr, uid, ids, field_name, arg, context)
    def _number_packages(self, cr, uid, ids, field_name, arg, context):
        return  self.pool.get('sale.order.line')._number_packages(cr, uid, ids, field_name, arg, context)
    def _get_1st_packaging(self, cr, uid, context={}):
        return  self.pool.get('sale.order.line')._get_1st_packaging(cr, uid, context={})
   
 
    _name='hotel_service.line'
    _description='hotel Service line'
    _inherits={'sale.order.line':'service_line_id'}
    _columns={
          'service_line_id':fields.many2one('sale.order.line','service_line_id',required=True,ondelete='cascade'),
          'folio_id':fields.many2one('hotel.folio','folio_id',ondelete='cascade'),
         
    }

    def create(self, cr, uid, vals, context=None, check=True):
        if not context:
            context={}
        if vals.has_key("folio_id"):
            folio = self.pool.get("hotel.folio").browse(cr,uid,[vals['folio_id']])[0]
            vals.update({'order_id':folio.order_id.id})
        roomline = super(osv.osv, self).create(cr, uid, vals, context)
        return roomline
    def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
        return  self.pool.get('sale.order.line').uos_change(cr, uid, ids, product_uos, product_uos_qty=0, product_id=None)
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        return  self.pool.get('sale.order.line').product_id_change(cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=partner_id,
            lang=False, update_tax=True, date_order=False)
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        return  self.pool.get('sale.order.line').product_uom_change(cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=partner_id,
            lang=False, update_tax=True, date_order=False)
    def on_change_checkout(self,cr, uid, ids, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'),checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'),context=None):
        qty = 1
        if checkout_date < checkin_date:
            raise osv.except_osv ('Error !','Checkout must be greater or equal checkin date')
        if checkin_date:
            diffDate = datetime.datetime(*time.strptime(checkout_date,'%Y-%m-%d %H:%M:%S')[:5]) - datetime.datetime(*time.strptime(checkin_date,'%Y-%m-%d %H:%M:%S')[:5])
            qty = diffDate.days
        return {'value':{'product_uom_qty':qty}}
    
    def button_confirm(self, cr, uid, ids, context={}):
       
        return  self.pool.get('sale.order.line').button_confirm(cr, uid, ids, context={})
    def button_done(self, cr, uid, ids, context={}):
        return  self.pool.get('sale.order.line').button_done(cr, uid, ids, context={})
    def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
        return  self.pool.get('sale.order.line').uos_change(cr, uid, ids, product_uos, product_uos_qty=0, product_id=None)
    def copy(self, cr, uid, id, default=None,context={}):
        return  self.pool.get('sale.order.line').copy(cr, uid, id, default=None,context={})
    
        

hotel_service_line()

class hotel_service_type(osv.osv):
    _name = "hotel.service_type"
    _inherits = {'product.category':'ser_id'}
    _description = "Service Type"
    _columns = { 
        'ser_id':fields.many2one('product.category','category',required=True,select=True),
        
    }
    _defaults = {
        'isservicetype': lambda *a: 1,
    }    
hotel_service_type()

class hotel_services(osv.osv):
    
    _name = 'hotel.services'
    _description = 'Hotel Services and its charges'
    _inherits={'product.product':'service_id'}
    _columns = {
        'service_id': fields.many2one('product.product','Service_id'),        
       
        }
    _defaults = {
        'isservice': lambda *a: 1,
        }
hotel_services()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
