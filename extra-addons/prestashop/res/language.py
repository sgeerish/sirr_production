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

class prestashop_lang(osv.osv):
    
    _name = 'prestashop.lang'
    _prestashop = True
    _prestashop_name = 'languages'
    
    _columns = {
                'name': fields.char('Name', size=32, required=True,
                        help="This field refers to Prestashop language name"),
                'language_code': fields.char('Code', size=5, required=True,
                         help="Display language code"),
                'active': fields.boolean('Active'),
                'iso_code': fields.char('ISO Code', size=2, required=True),
                'date_format_lite': fields.char('Date format', size=32,
                        required=True,
                        help="Date should be in mm/dd/yyyy format"),
                'date_format_full': fields.char('Date format (full)',
                        size=32,
                        required=True,
                        help="Date should be in mm/dd/yyyy with time format"),
                'is_rtl': fields.boolean('Is rtl?',
                        help="Is your language right to left or left to right?"
                             "(It's display your language direction.)"),
                'shop_ids':fields.many2many('sale.shop',
                        'lang_shop_rel',
                        'lang_id','shop_id',
                        'Shops',
                        help="Select your shop name"),
                'lang_id': fields.many2one('res.lang',
                        'Language',
                        help="This field refers to the OpenERP Language Class")
                }

    def get_int_ref(self, cr, uid, external_reference_id, presta_id,
                    context={}):
           
        """
            get_int_ref function is for mapping 
            the OpenERP ids to Prestashop ids for language 
                                            
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param external_reference_id: OperERP Shop reference,
            @param presta_id: getting reference of Prestashop id for language,
            @return: OpenERP id which is mapped to Prestashop id for language
            
        """
        
        openerp_id = False
        
        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name),
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
                
        if openerp_id and context.get('search_lang_id'):
            
            data = self.read(cr, uid, [openerp_id], ['lang_id'],
                            context=context)[0]
                            
            openerp_id = data['lang_id'] and data['lang_id'][0] or False

        return openerp_id

prestashop_lang()

class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    _prestashop = True
    _prestashop_name = 'customers'


res_partner()
