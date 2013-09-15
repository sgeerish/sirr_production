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

from osv import osv,fields
from openerp_prestashop_sync import utils
from tools.translate import _
import tools
import time
import pooler
import threading
import copy

class sale_shop(osv.osv):
    
    _inherit = 'sale.shop'


    def _get_config(self, cr, uid, ids, context):
        
        return True

    _columns = {
                'enable_prestashop':fields.boolean('Prestashop Enabled ?',
                         help="Check if you want to enable Prestashop"),
                'server_url':fields.char('Server URL',size=256,
                         help="Prestashop server URL"),
                'server_key':fields.char('Server Key',
                         size=256,
                         help="To accept all ssl"
                          "certificate without any certificate validation"),
                'validate_https':fields.boolean('Validate HTTPS',
                         help="Check if you want to validate https"),
                'prestshop_version':fields.char('Prestshop Version',
                         size=256,
                         help="Specify the version of prestashop"),
                'prestashop_config_path':fields.char('Configuration File Path',
                         size=256,
                         help="Set the system path to openerp.conf file"),
                'debug':fields.boolean('Debug?', 
                         help="Check if you want to debug"),
                'lang_ids':fields.many2many('prestashop.lang', 'lang_shop_rel',
                        'shop_id', 'lang_id',
                        'Language', 
                        help="Select Languages to be associated with the shop"),
                'verified':fields.boolean('Verified',
                          help="Automatically gets True"
                                "if connection is approved"),
                'product_ids': fields.many2many('product.product',
                        'sale_shop_product_tbl', 'shop_id', 'product_id',               
                        'Products',
                        help="Select Products to be associated with the shop"),
                'last_sync_date':fields.datetime('Last Synch Date',
                        help="Date when products were synchonized"),
                'last_image_sync_date':fields.datetime('Last Image Synch Date',
                       help="Date when Images were synchonized"),
                'categ_id':fields.many2one('product.category',
                                           'Product Home Category')
                }
    
    def get_presta_shop(self, cr, uid, ids, context):
        
        if not context:
            context = {}
            
        if not ids:
            return False
        
        if isinstance(ids, (list,tuple)):
            ids = ids[0]
            
        shop_data = self.read(cr, uid, ids, ['server_key', 'server_url',
                                          'debug', 'verified'], context=context)

        if not shop_data['verified'] :
            if not context.get('test'):
                #TODO Raise Exception for shop not verified
                return False

        connection = utils.prestashop.get([shop_data['server_url'],
                                           shop_data['server_key'],
                                           shop_data['debug'],
                                          ],context=context)

        return connection

    def test_connection(self, cr, uid, ids, context=None):
        
        context['test']=True
        
        connection = self.get_presta_shop(cr, uid, ids, context)
        res = connection.test_connection()
        
        if not res.get('errors'):
            raise osv.except_osv(_("Test Connection Was Successful"), '')
        
        else:
            raise osv.except_osv(
                 _("Connection test failed"),
                _("Reason: %s") % tools.ustr(res['errors']['error']['message'])
                 )
            
        return connection

    def approve_shop(self, cr, uid, ids, context=None):
        
        context['test']=True
        connection = self.get_presta_shop(cr, uid, ids, context)
        
        if self.get_presta_shop(cr, uid, ids, context):
            self.write(cr, uid, ids, {'verified':True})
            
        return True

    def get_products(self, cr, uid, ids, export_ids, context={}):
        
        result = {}
        
        if not isinstance(export_ids,(list,tuple)):
            export_ids = [export_ids]
            
        product_pool = self.pool.get('product.product')
        
        for self_obj in self.browse(cr, uid, ids, context=context):
            product_ids = [x.id for x in self_obj.product_ids]
            
            if export_ids:
               product_ids = list(set(product_ids) & set(export_ids))
               
            if not self_obj.last_sync_date:
                result[self_obj.id] = product_ids
                continue
            
            up_ids = []
            
            for product_id in product_ids :
                
                ext_id = product_pool.get_ext_ref(cr, uid, self_obj.id,                                                   
                                                  product_id, context=context)                                                 
                
                if not ext_id:
                    
                    up_ids.append(product_id)
                    
                    continue
                
                ref_id = self.pool.get('product.product').search(cr, uid, [ '|',
                                    ('write_date','>',self_obj.last_sync_date),
                                    ('create_date','=',False),
                                    ('id','=',product_id)])              
                
                if ref_id:
                    up_ids.append(product_id)

            result[self_obj.id] = up_ids
            
        return result

    def do_synch(self, cr, uid, ids, model_name, context={}):
        
        for shop_id in ids:
            self.pool.get(model_name).import_from_prestashop(cr, uid, shop_id,                                                    
                                                             context=context)
        return True

    def import_language(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True
        
        self.do_synch(cr, uid, ids, 'prestashop.lang', context=new_cnt)
        
        return {
                'name': _('Prestahop Languages'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'prestashop.lang',
                'context': {'active_test':False},
                'type': 'ir.actions.act_window',
                }
        
    def import_images(self, cr, uid, ids, context={}):
        
        self.do_synch(cr, uid, ids, 'image.types', context=context)
        
        for shop_id in ids:
            self.pool.get('image.image').import_image_prestashop(cr, uid, 
                                                                shop_id,
                                                                context=context)

        return True
    
    def export_images(self, cr, uid, ids, context={}):
        
        for shop_id in ids:
            image_ids = self.pool.get('image.image').get_updated_ids(cr, uid,                                                             
                                                                shop_id,
                                                                context=context)
            
            self.pool.get('image.image').export_image_products(cr, uid, shop_id,                                                                                                                           
                                                               image_ids,
                                                               context=context)
        return True

    def import_addresses_config(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True
        
        self.do_synch(cr, uid, ids, 'tr.presta.zone', context=new_cnt)
        self.do_synch(cr, uid, ids, 'res.country', context=new_cnt)
        self.do_synch(cr, uid, ids, 'res.country.state', context=new_cnt)
        self.do_synch(cr, uid, ids, 'res.partner.category', context=new_cnt)
        
        return True
    

    def import_account_config(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True
        
        self.do_synch(cr, uid, ids, 'account.tax', context=new_cnt)
        self.do_synch(cr, uid, ids, 'tax.rule.group', context=new_cnt)
        self.do_synch(cr, uid, ids, 'tax.rules', context=new_cnt)
        
        return True

    def import_product_categories(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True
        
        self.do_synch(cr, uid, ids, 'product.category', context=new_cnt)
        par_ids = self.pool.get('product.category').search(cr, uid, [
                                                      ('parent_id','=', False)])                                                                
        for par_id in par_ids:
            ext_id = self.pool.get('product.category').get_ext_ref(cr, uid,
                                                               ids[0], par_id,                                                               
                                                               context=context)
                        
	    read_data = self.pool.get('product.category').read(cr, uid, par_id,                                           
                                                        ['name'],
                                                        context=context)['name']
	   
            if ext_id and read_data == 'Home':
                
                self.write(cr, uid, ids, {'categ_id':par_id})
                
                parent_id = par_id
                
                break
            
        if parent_id:
            
            par_ids.remove(parent_id)
            self.pool.get('product.category').write(cr, uid, par_ids,                                           
                                                    {'parent_id': parent_id})
                                                               
        return True

    def import_product(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True
        
        self.do_synch(cr, uid, ids, 'product.product', context=new_cnt)
        self.do_synch(cr, uid, ids, 'product.combination', context=new_cnt)
        
        return True

    def import_product_attributes(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True

        self.do_synch(cr, uid, ids, 'prestashop.tag', context=new_cnt)
        self.do_synch(cr, uid, ids, 'product.features', context=new_cnt)
        self.do_synch(cr, uid, ids, 'product.feature.values', context=new_cnt)
        self.do_synch(cr, uid, ids, 'product.options', context=new_cnt)
        self.do_synch(cr, uid, ids, 'product.options.value', context=new_cnt)

        self.pool.get('res.partner')._prestashop_name = 'suppliers'
        new_cnt['ext_record'] = 'supplier'
        self.do_synch(cr, uid, ids, 'res.partner', context=new_cnt)

        new_cnt['ext_record'] = 'manufacturer'
        self.pool.get('res.partner')._prestashop_name = 'manufacturers'
        self.do_synch(cr, uid, ids, 'res.partner', context=new_cnt)

        return True

    def import_partner_addresses(self, cr, uid, ids, context={}):
        
        new_cnt = copy.deepcopy(context)
        new_cnt['read_at_once'] = True
        
        self.pool.get('res.partner')._prestashop_name = 'customers'
        new_cnt['ext_record'] = 'customer'
        
        self.do_synch(cr, uid, ids, 'res.partner', context=new_cnt)
        self.do_synch(cr, uid, ids, 'res.partner.address', context=new_cnt)
        
        return True

    def export_product(self, cr, uid, ids, context={}, export_ids=[]):
        
        for shop_id,product_ids \
        in self.get_products(cr, uid, ids, export_ids, context=context).items():                                         
                                                     

            tag_ids = self.pool.get('prestashop.tag').get_updated_ids(cr, uid,                                                              
                                                            shop_id,
                                                            context=context)            
            if tag_ids:
                self.pool.get('prestashop.tag').export_to_prestashop(cr, uid,                                                            
                                                             shop_id, tag_ids,                                                             
                                                             context=context)

            feature_ids = self.pool.get('product.features').get_updated_ids(cr,
                                                            uid,  shop_id,                                                           
                                                            context=context)
            
            if feature_ids:
                self.pool.get('product.features').export_to_prestashop(cr, uid,
                                                           shop_id, feature_ids,                                                
                                                           context=context)

            feature_value_ids = self.pool.get(
                                  'product.feature.values').get_updated_ids(cr,
                                                            uid, shop_id,                                                            
                                                            context=context)
            
            if feature_value_ids:
                self.pool.get('product.feature.values').export_to_prestashop(cr,
                                                             uid, shop_id,                                                             
                                                             feature_value_ids,
                                                             context=context)

            options_ids = self.pool.get('product.options').get_updated_ids(cr,
                                                             uid, shop_id,                                                               
                                                             context=context)
            
            if options_ids:
                self.pool.get('product.options').export_to_prestashop(cr, uid,                                                              
                                                              shop_id,
                                                              options_ids,
                                                              context=context)

            options_value_ids = self.pool.get(
                                  'product.options.value').get_updated_ids(cr,
                                                               uid, shop_id,                                                               
                                                               context=context)
            
            if options_value_ids:
                self.pool.get('product.options.value').export_to_prestashop(cr,
                                                            uid, shop_id,                                                            
                                                            options_value_ids,
                                                            context=context)

            cat_ids = self.pool.get('product.category').get_updated_ids(cr, uid,                                                            
                                                            shop_id,
                                                            context=context)
            
            if cat_ids:
                self.pool.get('product.category').export_to_prestashop(cr, uid,                                                           
                                                           shop_id, cat_ids,                                                           
                                                           context=context)

            self.pool.get('product.product').export_to_prestashop(cr, uid,                                                           
                                                          shop_id, product_ids,                                                          
                                                          context=context)

            self.write(cr, uid, shop_id, {
                        'last_sync_date': time.strftime("%Y-%m-%d %H:%M:%S")
                        })
            
        return True

    def import_sale_order(self, cr, uid, ids, context={}):
        
        for shop_id in ids:
            self.pool.get('sale.order').import_from_prestashop(cr, uid, shop_id,                                                 
                                                               context=context)

        return True
    
    def import_sale_order_update(self, cr, uid, ids, context={}):
        
        sale_ids = self.pool.get('sale.order').search(cr, uid, [
                                                    ('state','=','draft'),
                                                    ('presta_exported','=',True)
                                                               ])
        if sale_ids:

            self.pool.get('sale.order').update_status(cr, uid, sale_ids,                                             
                                                      context=context)

        return True

    def sync_all(self, cr, uid, ids, context={}):

        threaded_calculation = threading.Thread(target=self.sync_all_thread,
                                            args=(cr.dbname, uid, ids, context))
                                                          
        threaded_calculation.start()
        
        return True
    
    def sync_all_thread(self, cr, uid, ids, context={}):
        
        if cr:
            cr = pooler.get_db(cr).cursor()


        self.import_language(cr, uid, ids, context=context)
        self.import_addresses_config(cr, uid, ids, context=context)

        self.import_account_config(cr, uid, ids, context=context)
        self.import_product_categories(cr, uid, ids, context=context)
        self.import_product_attributes(cr, uid, ids, context=context)
        
        time.sleep(3)
        self.import_product(cr, uid, ids, context=context)

        self.import_partner_addresses(cr, uid, ids, context=context)
        self.export_product(cr, uid, ids, context=context)
        self.import_sale_order(cr, uid, ids, context=context)
        self.import_sale_order_update(cr, uid, ids, context=context)

        self.import_images(cr, uid, ids, context)
        self.export_images(cr, uid, ids, context)

        cr.commit()

        try:
            cr.close()
            
        except Exception:
            pass
        
        return True

sale_shop()
