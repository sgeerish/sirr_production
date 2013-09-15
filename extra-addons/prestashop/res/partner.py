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

class res_partner_category(osv.osv):
    
    """ 
        Partner Category class inherited for synchronize Partner Category
        with Prestashop.
    """
    _description='Partner Categories'
    _inherit = 'res.partner.category'
    _prestashop = True
    _prestashop_name = 'groups'

                                                                       
res_partner_category()


class res_partner_address(osv.osv):
    
    _description ='Partner Addresses'
    _inherit = 'res.partner.address'
    _prestashop = True
    _prestashop_name = 'addresses'
    
    _columns = {
                'last_name':fields.char('Last Name',size=64),
                }


res_partner_address()

class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'customers'

    _columns = {
                'is_manufacturer': fields.boolean('Manufacturer'),
                'lastname': fields.char('Last Name', size=32),
                'birthday': fields.date('Birthday'),
                'newsletter': fields.boolean('Newsletter'),
                'optin': fields.boolean('Option'),
                'is_guest': fields.boolean('Is Guest'),
                'is_carrier': fields.boolean('Is Carrier'),
                }
    
    _defaults = {
                 'is_carrier':False
                 }


    def read_from_prestashop(self, cr, uid, shop_id, openerp_ids,
                             context=None, convert_presta=False):
        
        if not context:
            context = {}
            
        if not self._prestashop:
            return False
        
        ret_val = []
        
        if not isinstance(openerp_ids, (list,tuple)):
            openerp_ids = [openerp_ids]
            
        shop_pool = self.pool.get('sale.shop')
        connection = shop_pool.get_presta_shop(cr, uid, shop_id,
                                               context=context)
        if convert_presta:
            ext_ids = [self.get_ext_ref(cr, uid, shop_id,  openerp_id,
                                        context) for openerp_id in openerp_ids]
                                            
        else:
            ext_ids = [openerp_id for openerp_id in openerp_ids]
            
        if connection and ext_ids:
            
            if context.get('read_at_once',False):
                
                rev_mapping,mapping_func = self.get_mapping_fields(cr, uid,
                                                               shop_id,                                                               
                                                               context=context,
                                                               reverse=True)
                
                read_mapping = rev_mapping.get('prestashop_read_mapping',False)
                
                del rev_mapping['prestashop_record_name']
                del rev_mapping['prestashop_read_mapping']
                
                if read_mapping:
                    
                    options = {
                               'display':str(eval(read_mapping)[context[
                                'ext_record']]+['id']).replace("'","").replace(
                                               "\n","").replace(" ","").strip()
                              }
                else:
                    
                    options = {
                       'display':str(rev_mapping.keys()+['id']).replace("'","")                                             
                               }
                    
                ret_val = connection.read_prestashop(self._prestashop_name,
                                                     ext_ids, options=options,
                                                     all_fields=False)
            else:
                ret_val = connection.read_prestashop(self._prestashop_name,
                                                     ext_ids)
        return ret_val

    def set_ext_ref(self, cr, uid, external_reference_id,
                    openerp_id,presta_id, context={}):
        
        """ 
           set_ext_ref function is for mapping the OpenERP ids to Prestashop ids
            
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param external_reference_id: OperERP Shop reference,
            @param openerp_id: reference of OperERP id for respective object,
            @param presta_id: reference of Prestashop id for respective object,
            @return: True if successfully creation of external reference
            
        """
        
        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name+'.'+self._prestashop_name),
                    ('res_id', '=', openerp_id),
                    ('external_reference_id', '=', external_reference_id),
                ])
        
        if ref_ids:
            
            ref_pool.write(cr, uid, ref_ids, {'ext_id': presta_id})
            
        else:
            ref_pool.create(cr, uid, {
                               'res_model':self._name+'.'+self._prestashop_name,
                               'res_id':openerp_id,
                               'external_reference_id':external_reference_id,
                               'ext_id':presta_id,
                               })
            
        return True

    def get_ext_ref(self, cr, uid, external_reference_id, openerp_id,
                    context={}):
                    
        
        """ 
        get_ext_ref function is for mapping the OpenERP ids to Prestashop ids
        
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param external_reference_id: OperERP Shop reference,
        @param openerp_id: getting reference of OperERP id,
        @return: prestashop id which is mapped to openerp id
        
        """
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
        
        """ 
            get_int_ref function is for mapping
            the OpenERP ids to Prestashop ids
            
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param external_reference_id: OperERP Shop reference,
            @param presta_id: getting reference of Prestashop id,
            @return: OpenERP id which is mapped to Prestashop id
        
        """
        
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

    

res_partner()

