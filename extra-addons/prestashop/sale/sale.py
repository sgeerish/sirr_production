# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-TODAY Tech-Receptives Solutions Pvt. Ltd.
#                            (<http://www.techreceptives.com>)
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
from osv import osv, fields
import time
from ConfigParser import ConfigParser
import netsvc

class sale_order_state(osv.osv):
    
    _name = 'sale.order.state'
    _prestashop = True
    _prestashop_name = 'order_states'
    
    _columns = {
                'name':fields.char('Name',size=64, translate=True),
                'template':fields.char('Template',size=64, translate=True),
                'send_mail':fields.boolean('Send Mail',
                                       help="Check if you want to send email"),
                'logable':fields.boolean('Logable',
                                      help="Check if you want to create logs"),
                'invoice':fields.boolean('Invoice'),
                'delivery':fields.boolean('Delivery'),
                }
    
    _defaults = {
                 'send_mail':True,
                 'logable':True,
                 'invoice':True,
                 'delivery':True,
                 }
    
    def import_from_prestashop(self, cr, uid, ids, context={},
                               convert_presta=False):
        convert_presta = False
        shop_id = 1
        
        return super(sale_order_state,
                     self).import_from_prestashop(cr, uid, shop_id,
                                                  context=context)                                         

    def export_to_prestashop(self, cr, uid, ids, context={},
                               convert_presta=False):
        convert_presta = False
        shop_id = 1
        return super(sale_order_state,
                     self).export_to_prestashop(cr, uid, shop_id, ids,                                         
                                                context=context)

sale_order_state()

class sale_order_line(osv.osv):
    
    _inherit = 'sale.order.line'
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'order_details'

    def import_from_prestashop(self, cr, uid, shop_id, ids, context={},
                               convert_presta=False):
        convert_presta = False
        shop_id = 1
        return super(sale_order_line,
                     self).import_from_prestashop(cr, uid, shop_id, ids,                                    
                                                  context=context)

    def _get_uom(self, cr, uid, shop_id, product_id, context=None):
        
        product_pool = self.pool.get('product.product')
        product_id = product_id and \
                     product_pool.get_int_ref(cr, uid, shop_id,
                                              product_id.get('_text',False),
                                              context=context)
        
        product_obj = product_pool.browse(cr, uid, product_id)
        
        if product_obj:
            
            return product_obj.uom_id.id
        
        return []

    def get_sale_order_data_prestashop(self, cr, uid, shop_id, ids=[],
                                       context={}):
        result = []

        logger = netsvc.Logger()

        read_preasta_datas = self.read_from_prestashop(cr, uid, shop_id, ids,
                                                       context=context,
                                                       convert_presta=False)

        trans_pool = self.pool.get('ir.translation')
        fields_get = self.fields_get(cr, uid, context=context)

        for openerp_data in self.get_openerp_data(cr, uid, shop_id,
                                                  read_preasta_datas,
                                                  context=context):
            
            temp_dict = {}
            
            presta_id = openerp_data['ext_id']
            other_trans = []

            fields_translate = [x for x in fields_get \
                        if fields_get[x].get('translate',
                                         False) and x in openerp_data.keys()]
            
            for field in fields_translate:

                translations = self._conver_translation(cr, uid, shop_id,
                                                        openerp_data[field])
                
                openerp_data[field] = translations['en_US']
                other_trans.append((translations, field))

            openerp_id = self.get_int_ref(cr, uid, shop_id,
                                        openerp_data['ext_id'], context=context)
                                          
            if openerp_id:
                result.append([1,openerp_id,openerp_data])

            else:
                ext_id = openerp_data['ext_id']
                del openerp_data['ext_id']
                result.append([0,0,openerp_data])

        return result

    def get_openerp_data(self, cr, uid, shop_id, presta_dicts, context=None):
        
        final_result = []
        
        if not context:
            context = {}
            
        if not self._prestashop:
            return final_result
        
        if not isinstance(presta_dicts, (list,tuple)):
            presta_dicts = [presta_dicts]
            
        rev_mapping,mapping_func = self.get_mapping_fields(cr, uid, shop_id,                                                           
                                                           context=context,
                                                           reverse=True)
        
        record_name = rev_mapping['prestashop_record_name']
        del rev_mapping['prestashop_record_name']
        
        for presta_dict in presta_dicts:
            
            result = {}
            presta_dict = presta_dict['order_detail']
            
            if  presta_dict['tax_rate']:
                tax_rate = float(presta_dict['tax_rate'])/100
                tax_ids = self.pool.get('account.tax').search(cr, uid,
                                       [('name','=', presta_dict['tax_name']),
                                        ('amount','=',tax_rate)])
                
                result['tax_id'] = [[6,0,tax_ids]]
                
            if record_name in presta_dict:
                presta_dict = presta_dict[record_name]
                
            mapping_val = presta_dict
            mapping_value = eval(mapping_func)
            
            presta_dict.update(dict([(x,y) for x,y in mapping_value.items() \
                                           if x not in presta_dict]))
            
            if not mapping_value['id_order']:
                mapping_value = eval(mapping_func)

            for k,v in presta_dict.items():
                
                if k == 'id':
                    result['ext_id'] = v
                    
                if k not in rev_mapping:
                    continue
                
                result[rev_mapping[k]] = v
                
                if k in mapping_value:
                    result[rev_mapping[k]] = mapping_value[k]
                    
            final_result.append(result)
            
        return final_result
    
sale_order_line()

class sale_order(osv.osv):
    
    _inherit = 'sale.order'
    _prestashop = True
    _prestashop_name = 'orders'
    
    _columns = {
            'invoice_number':fields.char('Invoice Number', size=64),
            'delivery_number':fields.char('Delivery Number', size=64),
            'secure_key':fields.char('Secure_key', size=132,
                                      help="Write your prestashop secure key"),
            'payment':fields.char('Payment', size=64),
            'gift_message':fields.char('Gift Message', size=64,
                                    help="Specify Gift Message if any"),
            'shipping_number':fields.char('Shipping Number', size=64,
                                    help="Specify the shipping number"),
            'invoice_date':fields.datetime('Invoice Date'),
            'delivery_date':fields.datetime('Delivery Date'),
            'conversion_rate':fields.float('Conversion Rate',
                                    help="Specify the current conversion rate"),
            'recyclable':fields.boolean('Recyclable', 
                                    help="Check if it is recyclable"),
            'gift':fields.boolean('Gift', help="Check if it's a Gift"),
            'current_state_id':fields.many2one('sale.order.state',
                                    'Current State',
                                    help="Select a current order state"),
            'total_discounts':fields.float('Total Discounts'),
            'total_paid':fields.float('Total Paid'),
            'total_paid_real':fields.float('Total Real Paid '),
            'total_products':fields.float('Total Products'),
            'total_products_wt':fields.float('Total Weight'),
            'total_shipping':fields.float('Total Shipping'),
            'carrier_tax_rate':fields.float('Carrier Tax Rate'),
            'total_wrapping':fields.float('Total Wrapping'),
            'presta_exported':fields.boolean('Exported',
                                    help="Export to prestashop"),
                }

    def set_ext_ref(self, cr, uid, external_reference_id,
                    openerp_id, presta_id, context={}):
        
        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name),
                    ('res_id', '=', openerp_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            ref_pool.write(cr, uid, ref_ids, {'ext_id':presta_id})
            
        else:
            ref_pool.create(cr, uid, {
                                'res_model':self._name,
                                'res_id':openerp_id,
                                'external_reference_id':external_reference_id,
                                'ext_id':presta_id,
                                     })
            
        return True

    def _get_price_list(self,cr, uid, shop_id, context):
        
        pricelist_id = self.pool.get('sale.shop').read(cr, uid, shop_id,
                                                      ['pricelist_id'], context)                                                       
        
        if pricelist_id.get('pricelist_id',False):
            return pricelist_id['pricelist_id'][0]
        
        return False
    
    def update_status(self, cr, uid, ids, context={}):
        
        self._update_status(cr, uid, 1, ids, context)
        
        return True

    def _update_status(self, cr, uid, shop_id, ids, context={}):
        
        state_mapping = self.get_state_mapping(cr, uid, shop_id, context)
        wf_service = netsvc.LocalService("workflow")
        
        for self_obj in self.browse(cr, uid, ids, context=context):
            
            if self_obj.current_state_id.name in state_mapping:
                
                if self_obj.state \
                in state_mapping[self_obj.current_state_id.name]:
                    
                    wf_service.trg_validate(uid, 'sale.order', self_obj.id,
                                            state_mapping[
                                            self_obj.current_state_id.name][
                                                      self_obj.state][-1],cr)                                                           

    def get_state_mapping(self, cr, uid, shop_id, context=None):

        result = {}
        
        if not context:
            context = {}
            
        shop_pool = self.pool.get('sale.shop')
        shop_data = shop_pool.read(cr, uid, shop_id,
                                   ['prestashop_config_path'])
        
        if not shop_data['prestashop_config_path'] or  \
           not shop_data['prestashop_config_path'].endswith(".conf") or\
           not self._prestashop:
            
            return result,False
        
        config = ConfigParser()
        config.read(shop_data['prestashop_config_path'])
        
        if not self._name in config.sections():
            
            return result,False
        
        mapping = dict(config.items(self._name))
        
        return eval(mapping['state_mapping'])

    def _set_associations(self, cr, uid, shop_id, associations, context={}):
        
        partner_id = self.pool.get('res.partner').get_int_ref(cr, uid, shop_id,                                       
                                associations['id_customer'].get('_text',False),                                                          
                                context=context) or False,
                                              
        lang_id = self.pool.get('res.lang').get_int_ref(cr,  uid,  shop_id,                                   
                                associations['id_lang'].get('_text',False),                                                        
                                context=context) or False,
                                                        
        asscociat = associations['associations']['order_rows']
        
        final_list = []
        
        if not asscociat or  not asscociat.get('order_row',False):
            
            return False
        
        order_ext_id = self.pool.get('sale.order').get_int_ref(cr, uid, shop_id,
                                                             associations['id'],
                                                             context=context)
        order_rows = asscociat['order_row']
        
        if isinstance(order_rows ,(list,tuple)):
            order_rows = order_rows
            
        else:
            order_rows = [order_rows]
            
        product_pool = self.pool.get('product.product')
        saleorder_line_pool = self.pool.get('sale.order.line')
        
        pricelist_id = self._get_price_list(cr, uid, shop_id, context)
        order_detail_ids = []
        
        for order_row in order_rows:
            order_detail_ids.append(order_row['id'])
            
        order_shipping = {}
        
        if associations['total_shipping'] > 0.0:
            
            order_shipping.update({
                                   'name':'shipping charge',
                                   'price_unit':associations['total_shipping'],
                                   'product_id':False,
                                   'product_uom_qty':1,
                                   'product_uom':1
                                   })
            
            line_ids = (0,0,order_shipping)
            
            if order_ext_id:
                
                line_ids = self.pool.get('sale.order.line').search(cr, uid,
                                            [('order_id', '=', order_ext_id),
                                             ('name', '=', 'shipping charge'),
                                            ], context=context)
                
                line_ids = line_ids and (1, line_ids[0],
                                     order_shipping) or (0, 0, order_shipping)
                                                             

            final_list.append(line_ids)
            
            line_datas = self.pool.get(
                            'sale.order.line').get_sale_order_data_prestashop(
                                                              cr, uid, shop_id,                                                    
                                                              order_detail_ids,
                                                              context=context)
            
            for line_data in line_datas:
                
                if order_ext_id:
                    
                    line_ids = self.pool.get('sale.order.line').search(cr, uid,
                                   [('order_id','=', order_ext_id),
                                ('product_id', '=', line_data[-1]['product_id'])
                                   ],context=context)
                                                     
                    
                    if line_ids:
                        
                        line_data[0]=1
                        line_data[1]=line_ids[0]
                        
                final_list.append(line_data)

        result = final_list
        
        return result


sale_order()
