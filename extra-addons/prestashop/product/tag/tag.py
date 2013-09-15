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

class prestashop_tag(osv.osv):
    
    _description='Prestashop Tag'
    _name = 'prestashop.tag'
    _prestashop = True
    _prestashop_name = 'tags'
    
    _columns = {
                'name': fields.char('Name', size=32, required=True,
                                help="Show product name from prestashop side"),
                }
    
prestashop_tag()
