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

from lxml import etree
from osv import fields, osv
import utils
from tools.translate import _
import tools

class prestashop_installer(osv.osv_memory):
    
    _name = 'prestashop.installer'
    _inherit = 'res.config.installer'
    
    _columns = {
                'shop_id': fields.many2one('sale.shop', 'Shop', required=True,
                             help="Select your shop name"),
                'server_url':fields.char('Server URL', size=256, required=True,
                             help="Your pretsashop server url"),
                'server_key':fields.char('Server Key', size=256, required=True,
                             help="Write Your prestashop shop server key"),
                'validate_https':fields.boolean('Accept All SSL', required=True,
                             help="To accept all ssl certificate without" 
                                "any certificate validation"),
                'prestashop_config_path':fields.char('Configuration File Path',
                             size=256,
                             required=True,
                             help="Configuration path of prestashop mapping"),
                'debug':fields.boolean('Debug?',help="If you need debugging"),
                }
    
    def _get_path(self, cr, uid, name, context={}):
        
        path = ''
        
        import os
        
        curr_dir = os.curdir
        path = tools.config['addons_path']
        
        print __name__,path
        path = os.path.join(path,__name__.split(".")[0],"openerp.conf")

        return path

    _defaults = {
                 
                'enable_prestashop': lambda *a:True,
                'server_url':'http://localhost/prestashop',
                'prestashop_config_path': _get_path,
                
                }

    def create(self, cr, uid, vals, context=None):
        
        cr_id = super(prestashop_installer,self).create(cr, uid, vals,
                                                        context=context)

        return cr_id

    def test_connection(self, cr, uid, ids, context={}):
        
        shop_data = self.read(cr, uid, ids[0], context=context)
        
        connection = utils.prestashop.get([shop_data['server_url'],
                               shop_data['server_key'],
                               shop_data['debug'],

                              ],context=context)
        
        res = connection.test_connection()

        if not res.get('errors'):
            
            if not context.get('no_error'):
                
                raise osv.except_osv(_("Test Connection Was Successful"), '')
        else:
            
            raise osv.except_osv(                                
                 _("Connection test failed"),
                _("Reason: %s") % tools.ustr(res['errors']['error']['message']))                               
            
        return True

    def execute(self, cr, uid, ids, context={}):
        
        if not context:
            context={}
            
        context['no_error'] = True
        self.test_connection(cr, uid, ids, context)
        shop_obj = self.pool.get('sale.shop')
        vals = self.read(cr, uid, ids[0], [], context=context)
        shop_id = vals['shop_id']
        
        vals = {
                'server_url':vals['server_url'],
                'server_key':vals['server_key'],
                'validate_https':vals['validate_https'],
                'prestashop_config_path':vals['prestashop_config_path'],
                'debug':vals['debug'],
                'enable_prestashop':True,
                'verified':True,
                }
        
        shop_obj.write(cr, uid, [shop_id], vals)
        
        return super(prestashop_installer, self).execute(cr, uid, ids,
                                                         context=context)

prestashop_installer()
