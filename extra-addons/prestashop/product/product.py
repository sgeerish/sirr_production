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

from osv import osv
from osv import fields
from tools.translate import _
import netsvc


class product_supplierinfo(osv.osv):

    _inherit = "product.supplierinfo"
    
    _columns = {
                'manufacturer': fields.boolean('Is Manufacturer'),
                }

product_supplierinfo()

class product_category(osv.osv):
    
    _inherit = 'product.category'
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'categories'

    _columns = {
            'description':fields.text('Description', translate=True,
                              help="Product description related to categories"),
            'meta_keywords':fields.char('Meta Keywords', size=64, 
                                        translate=True),
            'meta_description':fields.char('Meta Description', size=64,
                                           translate=True),
            'link_rewrite':fields.char('Link Rewrite', size=64, translate=True),
            }
    
    def _get_parent(self, cr, uid, shop_id, self_obj, context={}):
        
        shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id,
                                                     context=context)
        if self_obj.id == shop_obj.categ_id.id:
            return '0'
        
        if not self_obj.parent_id:
            
            ext_id = self.get_ext_ref(cr, uid, shop_id, shop_obj.categ_id.id,
                                      context=context)
        else:
            ext_id = self.get_ext_ref(cr, uid, shop_id, self_obj.parent_id.id,
                                      context=context)
            
        return ext_id


    def export_to_prestashop(self, cr, uid, shop_id, ids, context={}):
        
        if not ids:
            return False
        
        context['lang'] = 'en_US'
        logger = netsvc.Logger()
        fields_get = self.fields_get(cr, uid,
                                 context=context)
        fields_translate = [x for x in fields_get \
                            if fields_get[x].get('translate',False)]
        
        new_ids = [[x] for x in ids]
        
        for ids in new_ids:
            
            for presta_data,openerp_id \
            in zip(self.get_prestashop_data(cr, uid, shop_id, ids, 
                      context=context,translation_fields=fields_translate),ids):
                                                                    
                presta_id = self.get_ext_ref(cr, uid, shop_id, openerp_id,
                                             context=context)
                if presta_id:
                    presta_data = self.write_to_prestashop(cr, uid, shop_id,
                                                openerp_id, presta_data,
                                                context, convert_presta=True)
                                                           
                    if  not presta_data or 'errors' in presta_data:
                        
                        self.pool.get('prestashop.log').register_log(cr, uid,
                                                                     shop_id,
                                                                     self._name,
                                                        _("Error While writing External Record for object %s Openerp ID %s Error %s"%(
                                                                  self._name,
                                                                  openerp_id, 
                                                                  presta_data)),
                                                             'error', 'export',
                                                             context=context)
                                                                
                        cr.commit()
                        
                        continue
                    
                    self.pool.get('prestashop.log').register_log(cr, uid, shop_id, self._name,
                                                                _("Record Write for %s openerp id %s External id %s"%(self._name,openerp_id, presta_id)),
                                                             'info', 'export', context=context)
                                                            
                else:
                    
                    presta_data = self.create_to_prestashop(cr, uid, shop_id,
                                               openerp_id, presta_data, context)
                    
                    if 'errors' in presta_data:
                        
                        self.pool.get('prestashop.log').register_log(cr, uid, shop_id, self._name,
                                                                _("Error While creating External Record for object %s Openerp ID %s Error %s"%(self._name,openerp_id, presta_data)),
                                                                 'error', 'export', context=context)
                                                                
                        cr.commit()
                        
                        continue
                    
                    self.pool.get('prestashop.log').register_log(cr, uid, shop_id, self._name,
                                                                _("Record Created for %s openerp id %s External id %s"%(self._name,openerp_id, presta_data)),
                                                             'info', 'export', context=context)                                                            
        cr.commit()
        
        return True

    def get_updated_ids(self, cr, uid, shop_id, context={}):
        
        up_ids = []
        
        openerp_ids = self.search(cr, uid, [], context=context, order='id')
        shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id,                                                     
                                                     context=context)
        
        if not shop_obj.last_sync_date:
            return openerp_ids

        for openerp_id in openerp_ids :
            
            if openerp_id == shop_obj.categ_id.id:
                continue
            
            ext_id = self.get_ext_ref(cr, uid, shop_id, openerp_id,                                       
                                      context=context)
            if not ext_id:
                
                up_ids.append(openerp_id)
                continue
            
            ref_id = self.search(cr, uid, [
                    '|',
                    ('write_date','>',shop_obj.last_sync_date),
                    ('create_date','>',shop_obj.last_sync_date),
                    ('id','=',openerp_id)
            ])
            
            if ref_id:
                up_ids.append(openerp_id)

        return up_ids

product_category()

class product_product(osv.osv):
    
    _inherit = 'product.product'
    _prestashop_name = 'products'
    _prestashop = True
    _associations = False
    _not_thread = True
    
    _columns = {

                'out_of_stock':fields.integer('Out Of Stock',
                                      help="Product is not available in stock"),
                'associations':fields.char('associations',size=1),
                'link_rewrite':fields.char('Link Rewrite', size=64,
                                           translate=True),
                'shop_ids': fields.many2many('sale.shop', 
                                             'sale_shop_product_tbl',
                                             'product_id', 'shop_id', 'Shops',
                                             help="Select your shop name" ),
                'presta_exportable':fields.boolean('Exportable',
                                 help="Determine the product is expotable to"  
                                      "prestashop or not"),
        
                'meta_keywords':fields.char('Meta Keywords', size=256,
                                            translate=True),
                'meta_description':fields.char('Meta Description', size=256,
                                               translate=True),
                'meta_title':fields.char('Meta Title', size=128, 
                                         translate=True),
                'location': fields.char('Location', size=64),
                'upc': fields.char('UPC', size=16),
                'available_later': fields.char('Available Later', size=256, 
                                               translate=True),
                'available_now': fields.char('Available Now', size=256, 
                                             translate=True),
                'unity': fields.char('Unity', size=256),
                'condition': fields.selection([
                                               ('new','New'),
                                               ('used','Used'),
                                               ('refurbished', 'Refurbished')], 
                                               'Condition'),
                'date_add': fields.date('Create Date',
                                    help="Product created date for prestashop"),
        
                'is_carrier': fields.boolean('Is Carrier'),
                'show_price': fields.boolean('Show Price'),
                'quantity_discount': fields.boolean('Qty. Discount',
                                             help="Show discount on quntity"),
                'customizable': fields.boolean('Customizable',
                                            help="To customize your product"),
                'on_sale': fields.boolean('On Sale',
                                  help="Put the product on sale on prestashop"),
                'online_only': fields.boolean('Online Only'),
                'available_for_order':fields.boolean('Available For Order',
                                 help="Product is available for order or not"),
                'wholesale_price': fields.float('wholesale_price',
                                                help="Show wholesaler price"),
                'minimal_quantity': fields.integer('Minimal Qty.',
                             help="Determine the minimum quantity of product"),
                'quantity': fields.integer('Quantity',
                               help="Determine the product quantity"),
                'additional_shipping_cost':fields.float('Additional Shipping Cost',
                                            help="To add a shipping price"),
                'width': fields.float('Width',help="To Decide image width"),
                'depth': fields.float('Depth',help="To Decide image depth"),
                'height': fields.float('Height',help="To Decide image height"),
        
                'tag_id': fields.many2one('prestashop.tag', 'Prestashop Tag',
                            help="Show the product tag form prestashop side"),
                'product_features_ids': fields.many2many('product.features',
                             'rel_prod_feature',
                             'product_ids',
                             'product_features_ids',
                             'Product Features',
                             help="Show the product features from prestashop"),
                'product_options_values_id': fields.one2many(
                                                     'product.options.value',
                                                    'product_id',
                                                    'Product Option Values'),
                'tax_rule_group_id': fields.many2one('tax.rule.group',
                                             'Tax Rule Group',
                                             help="Name for tax rule groups."),
                'combination_ids':fields.one2many('product.combination', 
                                          'product_id', 'Product Combinations'),
                                                  
                'write_date':fields.datetime('Write Date',
                              help="Product last updated date from prestashop"),
                'create_date':fields.datetime('Create Date',
                                   help="Product created date for prestashop"),
                'image_ids':fields.one2many('image.image', 'product_id',
                                            'Images')
    }
    
    _defaults = {
                 'is_carrier':False
                 }

    def _get_price_pricelist(self, cr, uid, shop_id, price, product, context={}):
        
        result = price
        pricelist = self.pool.get('sale.shop').browse(cr, uid, shop_id,                                              
                                               context=context).pricelist_id.id
                                                      
        new_price = self.pool.get('product.pricelist').price_get(cr, uid,
                                                      [pricelist], product, 1.0)
                                                                 
        result = new_price[pricelist] or result

        return result

    def _set_associations_attribute(self, cr, uid, shop_id, associations,                                    
                                    context={}):
        
        if not associations or\
           not associations.get('product_options_values', False):
            
            return False
        
        if isinstance(associations['product_options_values'] ,(dict)):
            
            ext_id = associations['product_options_values']['id']
            
        else:
            
            lst = []
            
            for ext_id in associations['product_options_values']:
                
                lst.append(ext_id['id'])
                
        lst2 = []

        for val_id in lst:
            
            dic = {}
            
            val_obj = self.pool.get('product.options.value').browse(cr, uid,
                     self.pool.get('product.options.value').get_int_ref(cr,
                                    uid, shop_id, val_id, context=context))                                             
                                                        
            val = val_obj.name or ''
            opt_id = val_obj.prod_opt_id or False

            set_ext_ref(cr, uid, shop_id, val_id, presta_id, context={})

            dic = {'name': val,'prod_opt_id': opt_id.id}
            lst2.append([0,0,dic])
            
        return lst2

    def _set_associations_feature(self, cr, uid, shop_id, associations,
                                  context={}):
       
        if not associations or not associations.get('product_feature',False):
            
            return []

        if isinstance(associations['product_feature'] ,(dict)):
            
            ext_ids = associations['product_feature']['id']
            
        else:
            ext_ids = []

            for ext_id in associations['product_feature']:
                
                ext_ids.append(ext_id['id'])
                
        my_list = []
        
        for product_features_id in ext_ids:
            
            int_id = self.pool.get('product.features').get_int_ref(cr, uid,
                                  shop_id, product_features_id, context=context)
                                                                        
            if int_id:
                
                my_list.append(int_id)

        return [[6,0,my_list]]

    def _set_associations_tag(self, cr, uid, shop_id, associations, context={}):
        
        if not associations or  not associations.get('tag',False):
            
            return False
        
        if isinstance(associations['tag'] ,(dict)):
            
            ext_id = associations['tag']['id']
            
        else:
            
            ext_id = associations['tag'][0]['id']
            
        return self.pool.get('prestashop.tag').get_int_ref(cr, uid, shop_id,                                    
                                                        ext_id, context=context)

                                                           
    def _set_supplier(self, cr, uid, shop_id, ext_id, context={}):
        
        self.pool.get('res.partner')._prestashop_name  = 'suppliers'
        
        dic = {}
        
        if not ext_id:
            
            return []
        
        supplier_id = self.pool.get('res.partner').get_int_ref(cr, uid, shop_id,                                                      
                                                       ext_id, context=context)
        dic = {
               'name': supplier_id, 'min_qty': 1
               }
        
        return [[0,0,dic]]

    def _set_tax(self, cr, uid, shop_id, ext_id, context={}):
        
        if not ext_id:
            
            ext_id = []
            
        tax_id = self.pool.get('tax.rule.group').get_int_ref(cr, uid, shop_id,                                                   
                                                     ext_id, context=context)                                 

        return tax_id

    def _set_associations(self, cr, uid, shop_id, associations, context={}):
        
        if not associations or not associations.get('category',False):
            return False
        
        if isinstance(associations['category'] ,(dict)):

            ext_id = associations['category']['id']
        else:
            ext_id = associations['category'][0]['id']

        categ_id = self.pool.get('product.category').get_int_ref(cr, uid,
                                        shop_id, ext_id, context=context)
        
        return categ_id


# GET_ASSOCIATION DATA TO PRESTASHOP (EXPORT)

    def check_upc(self, cr, uid, shop_id, upc='', context={}):
        
        import sys;

        upc = ""
        numlist = ""
        convert_presta = False
        shop_id = 1
        
        if upc:
            
            if (len(upc)) <> 12:
                
                raise osv.except_osv(_('Error !'),
                          _('invalid UPC-A code!\nPlease Enter Valid UPC!'))
                sys.exit(1);
                
            else:
                result['upc'] = {
                         'id':self.pool.get('product.product').get_ext_ref(
                                   cr, uid, shop_id ,upc, context=context) or 1
                                 }
                
                if sum(numlist[0:6]) == sum(numlist[6:]):
                    
                    raise osv.except_osv(_('Error !'),
                             _('invalid UPC-A code!\nPlease Enter Valid UPC!'))
                    
                    sys.exit(1);

        return sum(numlist[0:6]) * 3

    def _get_associations(self, cr, uid, shop_id, self_obj, context={}):
       
        result = {
                  'categories':{},
                  'tags':{},
                  'product_features':{},
                  'product_option_values':{}
                  }
        #categories
        
        result['categories']['category']={
                  'id':self.pool.get('product.category').get_ext_ref(cr, uid,
                           shop_id, self_obj.categ_id.id, context=context) or 1}        
        
        result['tags']['tag']={'id':
                               self.pool.get('prestashop.tag').get_ext_ref(cr,
                                                       uid, shop_id,                                                       
                                                       self_obj.tag_id.id,
                                                       context=context) or 1}
        
        feature_pool = self.pool.get('product.features')
        feature_value_pool = self.pool.get('product.feature.values')
        
        feature_list = []
        
        if self_obj.product_features_ids:
            
            for feature_id in self_obj.product_features_ids:
                
                dic = {}
                
                ext_id = feature_pool.get_ext_ref(cr, uid, shop_id,
                                                  feature_id.id, 
                                                  context=context)
                
                for values in feature_id.feature_value_lines:
                    
                    dic = {'id': ext_id,'id_feature_value': {'id': 
                                         feature_value_pool.get_ext_ref(cr,
                                                            uid, shop_id,                                                            
                                                            values.id,
                                                            context=context)}}
                feature_list.append(dic)
                
        result['product_features']['product_feature']=feature_list

        return result

    def _get_tax(self, cr, uid, shop_id, self_obj, context={}):
        
        result = {
                  'id_tax_rules_group':{}
                  }
        
        if self_obj.tax_rule_group_id:
            result['id_tax_rules_group'] = self.pool.get(
                                             'tax.rule.group').get_ext_ref(cr,
                                               uid, shop_id,                                               
                                               self_obj.tax_rule_group_id.id,
                                               context=context)
                                             
        return result['id_tax_rules_group']

    def _get_supplier(self, cr, uid, shop_id, self_obj, context={}):
        
        result = {
                  'id_supplier':{}
                  }
        
        self.pool.get('res.partner')._prestashop_name  = 'suppliers'
        
        if self_obj.seller_ids:
            
            result['id_supplier']=self.pool.get(
                                    'res.partner').get_ext_ref(cr,
                                       uid, shop_id,
                                       self_obj.seller_ids[0].name.id,
                                       context=context) or {}
                                       
        return result['id_supplier']

product_product()

