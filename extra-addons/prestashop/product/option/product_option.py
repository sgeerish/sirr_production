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

class product_options(osv.osv):
    
    _name = 'product.options'
    _not_thread = True
    _prestashop = True
    _prestashop_name = 'product_options'
    
    _columns = {
                'name': fields.char('Name', size=32, required=True,
                                    translate=True),
                'public_name': fields.char("Public Name",size=64, required=True,
                                           translate=True),
                'prod_opt_value_lines': fields.one2many("product.options.value",
                                           'prod_opt_id',
                                           "Product Option Value", 
                                           help="Select product option value"),
                'product_id': fields.many2one("product.product", "Product",
                                           help="Select product"),
                }                                       

product_options()

class product_options_value(osv.osv):
    
    _name = 'product.options.value'
    _prestashop = True
    _prestashop_name = 'product_option_values'
    
    _columns = {
                'name': fields.char('Name', size=32, required=True,
                                    translate=True),
                'prod_opt_id': fields.many2one("product.options",
                                   "Product Option Value",
                                   help="Select product option value"),
                'product_id': fields.many2one("product.product", "Product",
                                  help="Select product"),
                }                                            

product_options_value()
