# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-TODAY Tech Receptives (<http://www.techreceptives.com>).
#   
#    Authors : Kinner Vachhani  (Tech Receptives)
#    Concept : Parthiv Patel (Tech Receptives)
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
'''
    Synchronization logic of product and category
'''

from osv import fields, osv
import math

from tools.translate import _

class product_product(osv.osv):
    '''
        Product inherited and synched
    '''

    _inherit = 'product.product'
    _columns = {
        'prestashop_id': fields.integer('Prestashop product id'),
        'exportable': fields.boolean('Export to website'),
        'updated': fields.boolean('Product updated on Prestashop'),
    }

    _defaults = {
        'prestashop_id': lambda *a: 0,
        'exportable': lambda *a: True,
        'updated': lambda *a: False,
    }
    
    def write(self, cr, uid, ids, datas=None, context=None ):
        '''
            Base method overridden for custom approach
        '''
        # setting datas as Dict. if its None
        if not datas:
            datas = {}

        # setting context as Dict. if its None
        if not context:
            context = {}
        
        #Adding updated field in data dict. if it is not there
        if 'updated' not in datas:
            datas['updated'] = False
        
        return super(osv.osv, self).write(cr, uid, ids, datas, context)
    
    #end def write(self, cr, uid, ids, datas=None, context=None ):
    
    def copy(self, cr, uid, id, default=None, context=None):
        '''
            Copy method overidden
        '''

        # setting default as Dict. if its None
        if default is None:
            default = {}

        # setting context as Dict. if its None
        if not context:
            context = {}

        default = default.copy()
        default.update({'prestashop_id':'0', 'updated':False})
        return super(product_product, self).copy(cr, uid, id, default=default,
                    context=context)
        
    #end def copy(self, cr, uid, id, default=None, context=None):    
    
    def prestashop_sync(self, cr, uid, prod_ids, context=None):
        '''
            Creates and update product in prestashop 
        '''
        if not context:
            context = {}
        prod_new_cnt = 0
        prod_upd_cnt = 0
        prod_fail_cnt = 0

        prod_upd = {}
        prod_new = {}

        server_id = self.pool.get('prestashop.config') \
                    .search(cr, uid,[('prestashop_flag','=',True)], \
                    context=context)

        if not server_id:
            raise osv.except_osv(_('Error'), \
                        _('You must have one shop \
                            with Prestashop flag turned on'))

        server_obj = self.pool.get('prestashop.config') \
                     .browse(cr,uid,server_id[0])

        self.prestashop_server = self.pool.get('prestashop.config') \
                    .prestashop_connection(cr, uid, context=context)

        if not prod_ids:
            raise osv.except_osv(_('Products Already updated'), \
                                    _('No products to update.'))
        
        #set limit for set of products to be synchronize
        l = 50
        f = lambda v, l: [v[i * l:(i + 1) * l] \
            for i in range(int(math.ceil(len(v) / float(l))))]

        split_prod_id_arrays = f(prod_ids, l)
        prod_obj = self.pool.get('product.product')
        cat_obj = self.pool.get('product.category')
        pricelist_obj = self.pool.get('product.pricelist')
#        pl_default_id = self.prestashop_get_pricelist(cr, uid, context=context)
        
        for product_ids in split_prod_id_arrays:

            prod_new = {}
            prod_upd = {}

            for prod_id in product_ids:

                product_dic = {}

                product_data = prod_obj.read(cr, uid , prod_id, ['ean13', \
                    'qty_available', 'active', 'categ_id', \
                    'description', 'name', 'prestashop_id', \
                    'description_sale','weight_net', 'standard_price'])

                category_brow = cat_obj.browse(cr, uid, \
                                product_data['categ_id'][0], context=context)

                if not int(category_brow.updated):
                    cat_obj.prestashop_sync(cr, uid, \
                        [category_brow.id], context)
    
                    category_brow = cat_obj.browse(cr, uid, \
                        product_data['categ_id'][0], context)
                #end if not int(category_brow.updated):
                    
                product_price = pricelist_obj.price_get(cr, uid, \
                                [server_obj.price_list_id.id], \
                                prod_id, 1.0)
                product_dic['product'] = {
                    'ean13': product_data['ean13'] or '', 
                    'id_manufacturer': '0', 
                    'wholesale_price': product_data['standard_price'], 
                    'id_category_default': category_brow.prestashop_id,
                    'reduction_to': '', 
                    'id_supplier': '0', 
                    'reference': '', 
                    'reduction_percent': '', 
                    'on_sale': '0', 
                    'uploadable_files': '', 
                    'quantity_discount': '', 
                    'location': '',
                    'out_of_stock': '',
                    'indexed': '0',
                    'reduction_from': '',
                    'price': product_price[1],
                    'weight': product_data['weight_net'],
                    'reduction_price': '',
                    'active':product_data['active'],
                    'ecotax': '',
                    'id_tax': '0',
                    'supplier_reference': '',
                    'customizable': '',
                    'text_fields': '',
                    'quantity': product_data['qty_available'],
                    'id_color_default':'',
                    'id_product': product_data['prestashop_id'],
                }

                product_dic['translation'] = {
                    '1': {
                    'meta_description': '',
                    'link_rewrite':'nj_%s' % (product_data['id']),
                    'meta_title':'',
                    'meta_keywords':'',
                    'description':product_data['description'],
                    'available_now':'',
                    'id_lang':'1',
                    'description_short':product_data['description_sale'],
                    'available_later':'',
                    'name':product_data['name']
                }}

                if product_data['prestashop_id']:
                    prod_upd[str(product_data['id'])] = product_dic
                else:
                    prod_new[str(product_data['id'])] = product_dic
            #endfor prod_id in product_ids:
            
            if prod_upd:
                result_data = self.prestashop_server.update_product(prod_upd)

                prod_obj.write(cr, uid, \
                    result_data, {'updated':True}, context)

                prod_upd_cnt = len(result_data)
#                prod_upd_cnt = len(result_data['updated'])
#                prod_fail_cnt = len(result_data['error'])
            #endif
            
            if prod_new:
                result_data = self.prestashop_server.create_product(prod_new)

                for openerp_id, prestashop_id in result_data['created'].iteritems():
                    self.write(cr, uid, [int(openerp_id)], \
                            datas={'updated':True, \
                            'prestashop_id':str(prestashop_id)}, \
                            context=context)

                #endfor
                 
                prod_new_cnt += len(result_data['created'].keys())
                prod_fail_cnt += len(result_data['error'])
                
            #endif
        #endfor product_ids in split_prod_id_arrays:
        
        return {'prod_new':prod_new_cnt, \
                'prod_update':prod_upd_cnt, \
                'prod_fail':prod_fail_cnt}
        #end def prestashop_sync(self, cr, uid, prod_ids, context=None):
product_product()


class product_category(osv.osv):
    '''
        Product Category inherited class for prestashop
    '''

    _inherit = 'product.category'
    _columns = {
        'prestashop_id': fields.integer('Prestashop category id'),
        'exportable': fields.boolean('Active on Prestashop'),
        'updated': fields.boolean('Category updated on Prestashop'),
        'description':fields.text('Description', \
            translate=True, help='Description of product in prestashop'),
    }

    _defaults = {
        'prestashop_id': lambda *a: 0,
        'exportable': lambda *a: True,
        'updated': lambda *a: False,
    }

    def write(self, cr, uid, ids, datas = None, context = None ):
        '''
            Base method overridden for custom approach
        '''
        # setting datas as Dict. if its None
        if not datas:
            datas = {}

        # setting context as Dict. if its None
        if not context:
            context = {}

        if 'updated' not in datas:
            datas['updated'] = False
        return super(osv.osv, self).write(cr, uid, ids, datas, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        '''
            Copy method overidden
        '''
        # setting default as Dict. if its None
        if not default:
            default = {}

        # setting context as Dict. if its None
        if not context:
            context = {}

        default = default.copy()
        default.update({'prestashop_id':'0', 'updated':False})
        return super(product_category, self).copy(cr, uid, id, default=default,
                    context=context)

    def synch_cat(self, cr, uid, category, context=None):
        '''
            Creates and update category in prestashop 
        '''
        # setting context as Dict. if its None
        if not context:
            context = {}

        if(category.parent_id and (category.parent_id.updated == False)):
            self.synch_cat(cr, uid, category.parent_id, context)

            category = self.browse(cr, uid, category.id, context=context)

            parent_id = category.parent_id.prestashop_id
        else:
            if(category.parent_id):
                parent_id = category.parent_id.prestashop_id
            else:
                parent_id = 1 #home Category

        level_depth = 1
        current_category = category
        while(current_category.parent_id):
            level_depth += 1
            current_category = current_category.parent_id
        category_data = {
                'category':{
                    'active':category.exportable,
                    'id_parent':parent_id,
                    'level_depth':level_depth,
                    'id_category':category.prestashop_id,
                    },
                'translation':{
                    '1':{
                        'name':category.name,
                        'description':category.description,
                        'link_rewrite':'nj_%s' % (category.id,),
                        'meta_title':'',
                        'meta_keywords':'',
                        'meta_description':'',
                        }
                    }
                }

        if(category.prestashop_id):
            if (category.updated):
                return True
            return_data = self.prestashop_server.update_category(category_data)
            self.categ_update += 1
        else:
            return_data = self.prestashop_server.create_category(category_data)
            self.write(cr, uid, [category.id], \
                                        {'prestashop_id':return_data}, \
                                        context=context)
            self.categ_new += 1

        self.write(cr, uid, [category.id], \
                            {'updated':'true'}, context=context )
        cr.commit()

        return True

    def prestashop_sync(self, cr, uid, categ_ids, context=None):
        '''
            Function called from wizard which takes categ ids for synchronization
        '''
        # setting context as Dict. if its None
        if not context:
            context = {}

        #counters for synch status
        self.categ_new = 0
        self.categ_update = 0
        self.categ_fail = 0

        self.prestashop_server = self.pool.get('prestashop.config')\
                            .prestashop_connection(cr, uid, context=context)

        self.category_ids = categ_ids
        for catid in self.category_ids:
            category = self.browse(cr, uid, catid, context=context)
            self.synch_cat(cr, uid, category, context=context)

        return {'categ_new':self.categ_new, 'categ_update':self.categ_update, \
                                                'categ_fail':self.categ_fail }

product_category()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
