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

class combinations(osv.osv):
    
    _name = 'product.combination'
    _prestashop = True
    _prestashop_name = 'combinations'
    _rec_name = 'reference'
    _not_thread = True

    _columns = {
            'reference':fields.char('Reference', size=64),
            'supplier_reference':fields.char('Supplier Reference', size=32),
            'location':fields.char('Location', size=64),
            'ean13':fields.char('Ean13', size=13),
            'upc':fields.char('UPC', size=12),
            'wholesale_price':fields.float('Wholesale Price'),
            'price':fields.float('Price'),
            'ecotax':fields.float('ecotax'),
            'quantity':fields.integer('Quantity'),
            'weight':fields.float('Weight'),
            'default_on':fields.integer('default_on'),
            'associations':fields.char('associations', size=1),
            'product_id':fields.many2one('product.product', 'Products'),
            'line_ids':fields.one2many('product.combination.lines',
                                       'combination_id', 'Combinations Lines'),
            'associations':fields.char('associations',size=1),
            }

    def import_from_prestashop1(self, cr, uid, ids, context={},
                               convert_presta=False):
        convert_presta = False
        shop_id = 1
        
        return super(combinations,self).import_from_prestashop(cr, uid, shop_id,                                                               
                                                               context=context)
        
    def export_to_prestashop1(self, cr, uid, ids, context={}):
        
        shop_id = 1

        return super(combinations, self).export_to_prestashop(cr, uid, shop_id,                                                            
                                                          ids, context=context)                                                              

    def set_lines(self, cr, uid, shop_id, product_options, combination_id):
        
        result=[]
        
        if not product_options \
        or not product_options.get('product_option_value', False):
        
            return []
        
        if not isinstance(product_options['product_option_value'],(list,tuple)):
            
            product_options[
             'product_option_value'] = [product_options['product_option_value']]                                                   
                                                       
        comb_int_id = self.get_int_ref(cr, uid, shop_id, combination_id)
        ext_ids = []
        
        if comb_int_id:
            
            lines = self.browse(cr, uid, comb_int_id).line_ids
            ext_ids = [x.options_value_id.id for x in lines \
                                             if x.options_value_id]
            
        for options in product_options['product_option_value']:
            
            option_val_id = self.pool.get(
                              'product.options.value').get_int_ref(cr, uid,                                                              
                                                       shop_id, options['id'])
                                                           
            new_dict = {}
            
            if option_val_id and option_val_id not in ext_ids:
                
                new_dict['options_value_id']=option_val_id
                op_id = self.pool.get('product.options.value').browse(cr, uid,                                                                      
                                                      option_val_id).prod_opt_id
                                                      
                new_dict['option_id'] = op_id and op_id.id or False
                result.append([0,0,new_dict])
                
        return result
    
    def get_lines(self, cr, uid, shop_id, self_obj):
        
        result = []
        
        for line in self_obj.line_ids:
            
            ext_id = self.pool.get('product.options.value').get_ext_ref(cr, uid,                                                            
                                              shop_id, line.options_value_id.id)
                                                            
            result.append({
                           'id': ext_id
                           })
            
        if result:
            
            return {'product_option_values':{'product_option_value':result}}
        
        return {}

combinations()

class combinations_line(osv.osv):
    
    _name = 'product.combination.lines'
    _description = 'Combinations lines'
    
    _columns = {
                'combination_id':fields.many2one('product.combination',
                            'Combination', help="Show the product combination"),
                'options_value_id':fields.many2one('product.options.value',
                                                   'Options Value'),
                'option_id':fields.many2one('product.options','Options'),
                }

combinations_line()

class product_features(osv.osv):
    
    _name = 'product.features'
    _not_thread = True
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'product_features'

    _columns = {
                
                'name':fields.char('Name', size=64, translate=True),
                'feature_value_lines':fields.one2many('product.feature.values', 
                                'feature_id','Feature Values', 
                                help="Show the feature of product")
                }

    def import_from_prestashop1(self, cr, uid, ids, context={},
                               convert_presta=False):
        
        convert_presta = False
        shop_id = 1
        
        return super(product_features, self).import_from_prestashop(cr, uid,
                                                    shop_id, context=context)

product_features()

class product_feature_values(osv.osv):
    
    _name = 'product.feature.values'
    _prestashop = True
    _prestashop_name = 'product_feature_values'

    _columns = {
                
                'name':fields.char('Name', size=64, translate=True),
                'custom':fields.boolean('Custom'),
                'feature_id':fields.many2one('product.features',
                         'Product Features', help="Show the feature of product")                                         
                }

    def import_from_prestashop1(self, cr, uid, ids, context={},
                               convert_presta=False):
        
        convert_presta = False
        shop_id = 1
        
        return super(product_feature_values, self).import_from_prestashop(cr, 
                                                  uid, shop_id, context=context)
    
product_feature_values()
