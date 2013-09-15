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
import tempfile
import os
from ConfigParser import ConfigParser
import base64
import threading
import pooler
import time

class image_type(osv.osv):
    
    _name = 'image.types'
    _description = 'Image Type'
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'image_types'

    _columns = {
                'name':fields.char('Name', size=256,
                               help="Product image name(e.g.small,large,etc.)"),
                'width':fields.integer('Width'),
                'height':fields.integer('Height'),
                'categories':fields.boolean('Categories',
                               help="Image type is using in product category"),
                'products':fields.boolean('Products',
                               help="Image type is using in product"),
                'manufacturers':fields.boolean('Manufacturers'),
                'suppliers':fields.boolean('Suppliers'),
                'scenes':fields.boolean('Scenes', 
                               help="Image type is using in scenes"),
                'stores':fields.boolean('Stores', 
                               help="Image type is using in stores"),
                }

    def import_export_language(self, cr, uid, ids, context={}):
        
        self.import_from_prestashop(cr, uid, 1, )
        return True
    
    def export_language(self, cr, uid, ids, context={}):
        
        self.export_to_prestashop(cr, uid, 1, ids)
        return True
    
image_type()


class images_image(osv.osv):
    
    _name = 'image.image'
    _description = 'Images'
    _prestashop = True
    _prestashop_name = 'images'

    _columns = {
                'product_id':fields.many2one('product.product', 'Product',
                                              help="Product name"),
                'categ_id':fields.many2one('product.category', 'Category', 
                                            help="Product category"),
                'language_id':fields.many2one('prestashop.lang', 'Language', 
                            help="This fields refers to prestashop languages"),
                'manufacturer_id':fields.many2one('res.partner', 'Manufacturer', 
                                        domain=[('is_manufacturer','=',True)]),
                'supplier_id':fields.many2one('res.partner', 'Supplier',
                                          domain=[('supplier','=',True)]),
                'write_date':fields.datetime('Write Date'),
                'create_date':fields.datetime('Create Date', 
                                   help="Image created date from prestashop"),
                'attachment_id':fields.many2one('ir.attachment', 'File',
                                            help="Attach product image"),
                'type_id':fields.many2one('image.types', 'Image Type',
                                            help="Select image type"),
        	    'image_data':fields.related('attachment_id', 'datas', 
                        type='binary', string='Product Image', readonly=True),
                }
    
    def unlink(self, cr, uid, ids, context={}):
        
        res = super(osv.osv, self).unlink(cr, uid, ids, context=context)
        
        if not getattr(self,'_prestashop',False):
            return res
        
        for openerp_id in ids:
            
            ref_pool = self.pool.get('external.reference')
            ref_ids = ref_pool.search(cr, uid, [
                        ('res_model','ilike', self._name),
                        ('res_id', '=', openerp_id),
                    ])
            
            if ref_ids:
                
                ref_pool.unlink(cr, uid, ref_ids, context=context)
                
        return res

    def set_ext_ref(self, cr, uid, external_reference_id, openerp_id,            
                    presta_id, context={}):
                    
        
        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name+context.get('image_type','')),
                    ('res_id', '=', openerp_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            ref_pool.write(cr, uid, ref_ids, {'ext_id':presta_id})
            
        else:
            ref_pool.create(cr, uid, {
                'res_model':self._name+context.get('image_type',''),
                'res_id':openerp_id,
                'external_reference_id':external_reference_id,
                'ext_id':presta_id,
            })

        return True

    def get_ext_ref(self, cr, uid, external_reference_id,
                    openerp_id, context={}):
        
        presta_id = False

        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model',
                      context.get('image_type',False) and '=' or 'ilike',
                      self._name+context.get('image_type','')),
                    ('res_id', '=', openerp_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            
            ref_data = ref_pool.read(cr, uid,
                                     ref_ids, ['ext_id'],
                                     context=context)[0]
            presta_id = ref_data['ext_id']

        return presta_id

    def get_updated_ids(self, cr, uid, shop_id, context={}):
        
        up_ids = []
        openerp_ids = self.search(cr, uid, [], context=context)
        shop_obj = self.pool.get('sale.shop').browse(cr, uid,
                                                     shop_id, context=context)
        
        if not shop_obj.last_image_sync_date:
            return openerp_ids

        for openerp_id in openerp_ids :
            ext_id = self.get_ext_ref(cr, uid, shop_id,
                                      openerp_id, context=context)
            if not ext_id:
                
                up_ids.append(openerp_id)
                
                continue
            
            ref_id = self.search(cr, uid, [
                    '|',
                    ('write_date','>',shop_obj.last_image_sync_date),
                    ('create_date','>',shop_obj.last_image_sync_date),
                    ('id','=',openerp_id)
            ])
            
            if ref_id:                
                up_ids.append(openerp_id)

        return up_ids

    def get_int_ref(self, cr, uid, external_reference_id, presta_id,
                    context={}):                   
                    
        openerp_id = False
        
        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name+context.get('image_type','')),
                    ('ext_id', '=', presta_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            
            ref_data = ref_pool.read(cr, uid, ref_ids, ['res_id'],                                      
                                     context=context)[0]
                                     
            openerp_id = ref_data['res_id']
            
        if not openerp_id and context.get('search_prestashop_data'):
            
            openerp_id = self.search(cr, uid,
                                     context.get('search_prestashop_data'),
                                     context=context)
            
            if openerp_id:
                openerp_id = openerp_id[0]

        return openerp_id

    def get_mapping_fields(self, cr, uid, shop_id, context=None, reverse=False):
                            
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
        
        return eval(mapping.get('type_mapping',"[]"))

    def import_export_image(self, cr, uid, ids, context={}):
        
        self.import_export_image_products(cr, uid, 1, ids, context=context)
        
        return True

    def import_image_prestashop(self, cr, uid, shop_id, context={}):
        
        threaded_calculation = threading.Thread(
                                    target=self.import_image_prestashop_thread,
                                    args=(cr.dbname, uid, shop_id, context))
        threaded_calculation.start()

        return True

    def import_image_prestashop_thread(self, cr, uid, shop_id, context={}):
        
        if cr:
            
            cr = pooler.get_db(cr).cursor()
            
        ir_pool = self.pool.get('ir.attachment')
        connection = self.pool.get('sale.shop').get_presta_shop(cr, uid,                                                               
                                                    shop_id, context=context)                                                              
        
        image_types_vals = self.get_mapping_fields(cr, uid, shop_id,                                                   
                                                   context=context)
        
        for image_obj,img_vals in image_types_vals.items():
            
            ret = connection.get_image_ids('images', image_obj)
            
            if not isinstance(ret['images']['image'],(list,tuple)):
                ret['images']['image']=[ret['images']['image']]
                
            for img_dict in ret['images']['image']:
                
                res_id = img_dict['id']
                
                if image_obj != 'products':
                    img = connection.get_images_only('images',image_obj,res_id)
                    image_ids = res_id
                else:
                    img = connection.get_images('images',image_obj,res_id)
                    
		    if not isinstance(img['image']['declination'],(list,tuple)):
                
			img['image']['declination'] = [img['image']['declination']]
                    image_ids = [x['id'] for x in img['image']['declination']]
                    image_ids = list(set(image_ids))

                context['image_type'] = image_obj

                for img_data in image_ids:
                    
                    if image_obj == 'products':

                        img_ret = connection.get_image_data('images',image_obj,
                                                            res_id, img_data)
                        if img_ret.status_code == 500:
                            continue
                    else:
                        img_ret = img

                    att_id = ir_pool.create(cr, uid, {'datas_fname':img_data,
                                  'datas':base64.encodestring(img_ret.content),
                                  'name':img_data})
                    
                    product_id = self.pool.get(img_vals[0]).get_int_ref(cr, uid,                                                                        
                                               shop_id, res_id, context=context)                                                                        
                                                                    
                    int_img_ref = self.get_int_ref(cr, uid, shop_id, img_data,                                        
                                                   context=context)
                    if int_img_ref:
                        self.write(cr, uid, int_img_ref, {
                                                  'attachment_id':att_id,
                                                  img_vals[1]:product_id,})                               
                                    
                    else:
                        int_img_ref = self.create(cr, uid, {                                                 
                                                  'attachment_id':att_id,
                                                   img_vals[1]:product_id,
                                                  })
                        
                    self.set_ext_ref(cr, uid, shop_id, int_img_ref,
                                     img_data, context=context)
                    cr.commit()

        try:
            cr.close()
            
        except Exception:
            pass
        
        return True


    def export_image_products(self, cr, uid, shop_id, ids, context={}):
        
        threaded_calculation = threading.Thread(
                                target=self.export_image_products_thread,
                                args=(cr.dbname, uid, shop_id, ids, context))                                         
                                                      
                                                      
        threaded_calculation.start()

        return True

    def export_image_products_thread(self, cr, uid, shop_id, ids, context={}):
        
        if cr:
            
            cr = pooler.get_db(cr).cursor()
            
        openerp_data = {}
        
        for self_obj in self.browse(cr, uid, ids, context=context):
            
            image = self_obj.attachment_id.datas
            image_en = base64.decodestring(image)
            
            connection = self.pool.get('sale.shop').get_presta_shop(cr, uid,
                                                    shop_id, context=context)         
                                                                   
                                                             
            exs_ids = []
            
            if self_obj.product_id:
                
                context['image_type'] = 'products'
                p_id = self.pool.get('product.product').get_ext_ref(cr, uid,
                                                        shop_id,
                                                        self_obj.product_id.id,
                                                        context=context)
                if not p_id :
                    
                    continue
                
                ret = connection.get_images('images', 'products', p_id,)
                
                if  ret:
                    
                    ext_img_id = self.get_ext_ref(cr, uid, shop_id,
                                                  self_obj.id, context=context)

                    if ext_img_id:
                        connection.delete_images('images','products', p_id,
                                                  ext_img_id)
                        
		    if not isinstance(ret['image']['declination'],(list,tuple)):
                
			ret['image']['declination'] = [ret['image']['declination']]
            
                    exs_ids = list(set([int(x['id']) \
                                        for x in ret['image']['declination']]))
            elif self_obj.categ_id:
                
                context['image_type'] = 'categories'
                p_id = self.pool.get('product.category').get_ext_ref(cr, uid,
                                                        shop_id,
                                                        self_obj.categ_id.id,
                                                        context=context)
                if not p_id:                    
                    continue
                
                ret = connection.read_prestashop('images','categories','')[0][
                                                                       'images']
                
                ext_img_id = self.get_ext_ref(cr, uid, shop_id, self_obj.id,                                     
                                              context=context)
                
                exs_ids = list(set([int(x['id']) for x in  ret['image']]))

                if ext_img_id:
                    
                    connection.delete_images('images','categories',p_id)
            else:
                continue

            new_file = tempfile.NamedTemporaryFile(delete=False)
            new_file.write(image_en)
            file_name = new_file.name
            new_file.close()
            read_file = open(file_name,'r')

            data = {
                    'image':(self_obj.attachment_id.datas_fname, read_file)
                    }
            
            os.unlink(file_name)
            
            if context['image_type'] != 'products':
                
                r = connection.create_image('images', context['image_type'],                                            
                                            p_id, data)

                ret = connection.read_prestashop('images',
                                         context['image_type'],'')[0]['images']
                                         
                if not isinstance(ret['image'], (list,tuple)):
                    
                    ret['image'] = [ret['image']]

                after_ids = list(set([int(x['id']) for x in  ret['image']]))
                new_ids = list(set(after_ids) - set(exs_ids))
                
                if not new_ids:
                    
                    new_ids = exs_ids
                    
                if new_ids:
                    
                    self.set_ext_ref(cr, uid, context['image_type'],
                                     context['image_type'], self_obj.id,
                                     new_ids[0], context=context)
            else:
                
                connection.create_image('images', 'products', p_id, data)

                ret = connection.get_images('images','products',p_id)
                
		if not isinstance(ret['image']['declination'],(list,tuple)):
            
			ret['image']['declination'] = [ret['image']['declination']]
            
                after_ids = list(set([int(x['id'])\
                                      for x in ret['image']['declination']]))
                
                new_ids = list(set(after_ids) - set(exs_ids))
                
                if not new_ids:
                    
                    new_ids = exs_ids
                    
                if new_ids:
                    self.set_ext_ref(cr, uid, shop_id, self_obj.id, new_ids[0],                                      
                                     context=context)
            cr.commit()
            
        self.pool.get('sale.shop').write(cr, uid, shop_id, {                                        
                                         'last_image_sync_date':time.strftime(
                                                          "%Y-%m-%d %H:%M:%S")})                                         
        cr.commit()
        
        try:
            cr.close()
            
        except Exception:
            pass
        
        return True

images_image()

