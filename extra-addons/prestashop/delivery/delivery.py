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
from ConfigParser import ConfigParser
import copy
import threading
import pooler
from tools.translate import _
import netsvc
import time

class delivery_handlings(osv.osv):
    
    _name = 'delivery.handlings'
    _description = "delivery.handlings"
    _prestashop = True
    _prestashop_name = 'deliveries'
    
    _columns = {
                'carrier_id':fields.many2one('delivery.carrier',
                            'Carrier', help="Select an appropriate carrier"),
                'price_range_id':fields.many2one('delivery.grid.line',
                            'Price Range',
                            help="Select an appropriate price range"),
                'weight_range_id':fields.many2one('delivery.grid.line',
                            'Weight Range',
                            help="Select an appropriate weight range"),
                'zone_id':fields.many2one('tr.presta.zone','Zone', 
                            help="Select Zone"),
                'price':fields.float('Price')
                }
    

delivery_handlings()

class delivery_carrier(osv.osv):
    
    _inherit = "delivery.carrier"
    _description = "Carrier"
    _prestashop = True
    _prestashop_name = 'carriers'
    
    _columns={
              'url':fields.char('URL',size=128, help="Specify URL"),
              'is_free':fields.boolean('Is Free'),
              'delay':fields.char('Delay',size=128,translate=True),
              }
    
    def get_openerp_data(self, cr, uid, shop_id, presta_dicts, context=None):
        
        partner_pool =self.pool.get('res.partner')
        product_pool =self.pool.get('product.product')
        
        open_datas = super(delivery_carrier,self).get_openerp_data(cr,
                     uid, shop_id,presta_dicts, context=context)
        
        for open_data in open_datas:
            
            partner_ids = partner_pool.search(cr, uid,[
                                            ('name','=',open_data['name']),
                                             ('is_carrier','=',True)])
            if partner_ids:
                
                open_data.update({'partner_id': partner_ids[0]}) 
                
            else:
                
                open_data.update({'partner_id': partner_pool.create(cr, uid, 
                                   {'name':open_data['name']
                                           or 'Carrier','is_carrier':True}
                                )})
                
            product_ids = product_pool.search(cr, uid,
                                               [('name','=',open_data['name']),
                                                ('is_carrier','=',True)])
            
            if product_ids:
                
                open_data.update({'product_id': product_ids[0]}) 
                
            else:
                product_id = product_pool.create(cr, uid,
                                                  {'name':open_data['name']or
                                                   'Carrier','is_carrier':True,
                                                          'type':'service' })
                open_data.update({'product_id': product_id})
                
        return open_datas
        
    def import_from_prestashop_thread(self, cr, uid, shop_id,ids=[],context={},
                           convert_presta=False):
        
            if cr:
                
                cr = pooler.get_db(cr).cursor()
                
            logger = netsvc.Logger()
            
            if not ids:
                
                ids = self.search_from_prestashop(cr, uid, shop_id,
                                                  context=context)
                convert_presta = False
                
            read_preasta_datas = self.read_from_prestashop(cr, uid, shop_id, 
                                                  ids, context=context,
                                                  convert_presta=convert_presta)
            
            trans_pool = self.pool.get('ir.translation')
            
            fields_get = self.fields_get(cr, uid, context=context)
                                     
            for openerp_data in self.get_openerp_data(cr,uid, shop_id, 
                                    read_preasta_datas, context=context):
        
                presta_id = openerp_data['ext_id']
                other_trans = []
        
                fields_translate = [x for x in fields_get \
                        if fields_get[x].get('translate',False)\
                                            and x in openerp_data.keys()]
                
                for field in fields_translate:
        
                    translations = self._conver_translation(cr, uid, shop_id,
                                                            openerp_data[field])
                    
                    openerp_data[field] = translations['en_US']
                    other_trans.append((translations, field))
        
                new_cnt = copy.deepcopy(context)
                search_field = self._search_field
                
                if search_field:
                    
                    try:
                        
                        new_cnt['search_prestashop_data'] = eval(search_field)
                        
                    except Exception as e:
                        
                        logger.notifyChannel(_("Prestashop Sync"), 
                                                netsvc.LOG_ERROR,
                                             _("Erro in Eval of search field"))
                        print "ERRO IN EVAL",e
        
                openerp_id = self.get_int_ref(cr, uid, shop_id,
                                              openerp_data['ext_id'],
                                              context=new_cnt)
                
                if openerp_id:
                    
                    ext_id = openerp_data['ext_id']
                    del openerp_data['ext_id']
                    
                    self.write(cr, uid, [openerp_id], openerp_data, 
                               context=context)
                    
                    logger.notifyChannel(_("Prestashop Sync"), 
                         netsvc.LOG_INFO, _("Record Write for %s opener id %s External id %s"%(
                                                   self._name,openerp_id, ext_id)))
                    
                else:
                    try:
                        ext_id = openerp_data['ext_id']
                        del openerp_data['ext_id']
                        openerp_id = self.create(cr, uid, openerp_data,
                                                  context=context)
                        self.pool.get('delivery.grid').create(cr, uid, {
                                                    'name':openerp_data['name'],
                                                    'carrier_id':openerp_id})
                        
                        logger.notifyChannel(_("Prestashop Sync"), 
                                     netsvc.LOG_INFO,
                                         _("Record created for %s opener id %s External id %s"%(
                                                         self._name,openerp_id,ext_id)))
                    except Exception as e:
                        logger.notifyChannel(_("Prestashop Sync"),
                                              netsvc.LOG_ERROR, 
                                              _("Error in Creating new %s Values are %s error is %s"%(
                                                                      self._name, openerp_data, e)))
                        print "ERROR ::::::::",e
                        
                        cr.commit()
                        
                        continue
                    
                self.set_ext_ref(cr, uid, shop_id, openerp_id, presta_id,
                                 context)
                                 
                for trans_data,field in other_trans:
                    
                    for lang_data in trans_data:
                        
                        if lang_data == 'en_US':
                            continue
                        
                        trans_pool._set_ids(cr, uid, self._name+','+field,
                                            'model', lang_data, [openerp_id],
                                            trans_data[lang_data],
                                            openerp_data[field],
                        )
                cr.commit()
        
            try:
                cr.close()
                
            except Exception:
                pass
            
            return True
        
delivery_carrier()

class delivery_grid_line(osv.osv):
    
    _inherit = "delivery.grid.line"
    _description = "Delivery Grid Line"
    _prestashop = True
    _prestashop_name = 'weight_ranges'
    
    _columns = {
                'min_value':fields.float('Minimum Value'),
                }
    
    def set_ext_ref(self, cr, uid, external_reference_id, openerp_id,
                    presta_id, context={}):

        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name+'.'+self._prestashop_name),
                    ('res_id', '=', openerp_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            
            ref_pool.write(cr, uid, ref_ids, {'ext_id':presta_id})
            
        else:
            ref_pool.create(cr, uid, {
                'res_model':self._name+'.'+self._prestashop_name,
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
                    ('res_model','=', self._name+'.'+self._prestashop_name),
                    ('res_id', '=', openerp_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            ref_data = ref_pool.read(cr, uid, ref_ids, ['ext_id'],
                                     context=context)[0]
            presta_id = ref_data['ext_id']
    
        return presta_id
    
    def get_int_ref(self, cr, uid, external_reference_id,
                        presta_id, context={}):

        openerp_id = False
        ref_pool = self.pool.get('external.reference')
        
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name+'.'+self._prestashop_name),
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
    
    def import_weight_range(self, cr, uid, ids, context={}):
        
        self._prestashop_name = 'weight_ranges'
        context.update({'ext_record':'weight_range'})
        context.update({'type':'weight'})
        
        return super(delivery_grid_line,self).import_from_prestashop(cr, uid, 1,
                                                                context=context)
    
    def import_price_range(self, cr, uid, ids, context={}):
        
        self._prestashop_name = 'price_ranges'
        context.update({'ext_record':'price_range'})
        context.update({'type':'price'})
        
        return super(delivery_grid_line,self).import_from_prestashop(cr, uid, 1,
                                                       context=context)
    
    def get_openerp_data(self, cr, uid, shop_id, presta_dicts, context=None):
        
        open_datas = super(delivery_grid_line, self).get_openerp_data(cr, uid, 
                                                          shop_id, presta_dicts,                                        
                                                          context=context)
                           
        for open_data in open_datas:
            
            open_data.update({
                              'list_price':0.0,'standard_price':0.0
                              })
        return open_datas
    
delivery_grid_line()      
