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
    Tax Synchronisation of openerp and prestashop
'''

from osv import fields, osv
from tools.translate import _

class prestashop_tax(osv.osv):
    """
    A tax object.
        Inherited for prestashop synch
    
    """
    
    _inherit = 'account.tax'
    _columns = {
        'prestashop_id': fields.integer(_('Prestashop Tax id')),
        'updated': fields.boolean(_('Tax updated on Prestashop')),
    }
    
    _defaults = {
        'prestashop_id': lambda *a: 0,
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
    
    def prestashop_sync(self, cr, uid, tax_ids, context):
        '''
            Creates and update tax in openerp 
        '''
        
        if not context:
            context = {}
        
        server_id = self.pool.get('prestashop.config') \
                    .search(cr, uid,[('prestashop_flag','=',True)], \
                    context=context)

        if not server_id:
            raise osv.except_osv(_('Error'), \
                        _('You must have one shop \
                            with Prestashop flag turned on'))

        self.prestashop_server = self.pool.get('prestashop.config') \
                    .prestashop_connection(cr, uid, context=context) 
        
        prestashop_taxes = self.prestashop_server.getTaxes()

        return_obj = self.prestashop_tax_update(cr, uid,
                                                prestashop_taxes,
                                                context=context)
        
        return return_obj
    #end def prestashop_sync(cr, uid, tax_ids, context)
    
    def prestashop_tax_update(self, cr, uid, data, context={}):
        '''
            Create, update and delete tax in openerp
        '''
        
        tax_new_cnt = 0
        tax_upd_cnt = 0
        tax_del_cnt = 0
        
        #check for blank dict
        if not data:
            raise osv.except_osv(_('Tax synch error'), \
                                _('No taxes configure on prestashop'))
        #end if data:
        
        #get ids of all prestashop synch tax
        openerp_taxid = self.get_openerp_tax_dict(cr, uid, context)
        
        tax_fields = self.fields_get(cr, uid, context=context)
        not_default_fields = ('name', )
        default_fields = list(set(tax_fields.keys()) - set(not_default_fields))
        tax_default = self.default_get(cr, uid,
                                default_fields,
                                context=context)
        
        for presta_taxid in data.iterkeys():
            #datas to write in openerp
            write_data = {
                     'name': data[presta_taxid][1],
                     'amount': data[presta_taxid][0],
                     'prestashop_id': presta_taxid,
                     'updated': True,
                             }
            
            #if prestashop id in openerp then update
            if openerp_taxid and (presta_taxid in openerp_taxid.keys()):
                openerp_tax_id = self.search(cr, uid, 
                                [('prestashop_id', '=', presta_taxid)])
                self.write(cr, uid, openerp_tax_id, write_data, context)
                tax_upd_cnt += 1
            #else create a new tax
            else:
                tax_default.update(write_data)
                self.create(cr, uid, tax_default)
                tax_new_cnt += 1
            #end if presta_taxid in openerp_taxid: 
        #end for presta_taxid in data.iterkeys():
        
        #get deleted prestashop tax id
        del_tax_ids = list(set(openerp_taxid.keys())-set(data.keys()))
        del_tax_ids = self.get_value_from_key(cr, openerp_taxid, del_tax_ids)
        #delete tax in openerp
        self.unlink(cr, uid, del_tax_ids, context)
        tax_del_cnt = len(del_tax_ids)
        
        return {'tax_new':tax_new_cnt, \
                'tax_update':tax_upd_cnt, \
                'tax_del':tax_del_cnt}
    #end def prestashop_create_tax(self, cr, uid, data, context={}):
    
    def get_openerp_tax_dict(self, cr, uid, context):
        '''
            This function gives dictonary of {prestashop_id:tax_id}
        '''
        
        data_dict = {}

        openerp_taxid = self.search(cr, uid, [('prestashop_id', '<>', '0')])
        openerp_pres_data = self.read(cr, uid, 
                                      openerp_taxid,
                                      ['prestashop_id'], context)
        
        for i in openerp_pres_data:
            data_dict[str(i['prestashop_id'])] = i['id']
        #end for i in openerp_pres_data:
        
        return data_dict
    #end def get_prestashop_id_list(self,cr, uid, context):
    
    def get_value_from_key(self, cr, dict_data, list_keys):
        '''
            This functions gives list of value from dictonary
        '''
        
        return_list = []
        
        for data_key, data_value in dict_data.iteritems():
            if data_key in list_keys:
                return_list.append(data_value)
            #end if data_key in keys:
        #end for data_key, data_value in list:

        return return_list 
    #end def get_value_from_key(self, list, key):
    
prestashop_tax()
