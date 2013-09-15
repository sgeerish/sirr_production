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
    Configuration module of prestashop
'''

from osv import fields, osv
import xmlrpclib
import netsvc

from tools.translate import _

class prestashop_config(osv.osv):
    '''
        Prestashop basic configration object
    '''

    _name = 'prestashop.config'
    _rec_name = 'prestashop_name'
    _description = 'Prestashop Configuration'
    _columns = {
        'prestashop_flag':fields.boolean('Prestashop sync flag', 
            required=True, 
            help="The Prestashop active web must have this box checked."),
        'prestashop_name':fields.char('Prestashop connection name', 
            required=True, size=64),
        'prestashop_host':fields.char('Prestashop Web URL', size=64, 
            required=True, help="URL to Magento shop ending with /"),
        'price_list_id':fields.many2one('product.pricelist', 'Price List', required=True),
    }

    _defaults = {
        'prestashop_flag': lambda *a: True,
        'prestashop_host': lambda *a: 'http://localhost/',
    }
 
    def prestashop_connection(self, cr, uid, context=None):
        '''
            Prestashop connection function to get a connection object
        '''
        if not context:
            context = {}

        connect_logger = netsvc.Logger()
        
        try:
            prestashop_id = self.search(cr, uid,
                    [('prestashop_flag', '=', True)],
                    context=context)

            if len(prestashop_id) < 1 :
                raise osv.except_osv(_('UserError'),
                        _('You must have only one shop \
                            with Prestashop flag turned on'))
            else :
                prestashop_obj = self.browse(cr, uid, prestashop_id[0],
                                                      context=context)
                server = xmlrpclib \
                    .ServerProxy("%smodules/openerp/openerpsynchro.php"
                                    % prestashop_obj.prestashop_host)

        except Exception, error:

            connect_logger.notifyChannel(_("Connection Error with prestashop"),
                    netsvc.LOG_ERROR, _("Error : %s") % error)
            
            raise osv.except_osv(_("UserError"),
                    _("You must have a declared website with a valid URL"))
            

        return server

prestashop_config()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
