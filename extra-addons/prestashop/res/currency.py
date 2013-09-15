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

from osv import osv, fields

class res_currecny(osv.osv):
    
    _inherit = 'res.currency'
    _prestashop = True
    _prestashop_name = 'currencies'
    
    _columns = {
                'description':fields.char('Description',size=16),
                'iso_code_number':fields.char('Iso Code Number',size=3),
                'decimals':fields.boolean('Decimals'),
                'deleted':fields.boolean('Deleted'),
                'format':fields.char('Format',size=16),
                }
    
    _defaults = {
                 'decimals':lambda *a:True,
                 'deleted':lambda *a:False,    
                 }
    
    
res_currecny()
