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

class tr_presta_zone(osv.osv):
    
    _name = 'tr.presta.zone'
    _prestashop = True
    _prestashop_name = 'zones'
    _not_thread = True
    
    _columns = {
                'name':fields.char('Name',size=64),
                'active':fields.boolean('Active')
                }
    
    _defaults = {
                 'active':lambda *a:True,
                 }
    

tr_presta_zone()

class Country(osv.osv):
    
    _inherit = 'res.country'
    _not_thread = True
    _prestashop = True
    _prestashop_name = 'countries'
    
    _columns = {
                'contains_states':fields.boolean('Contain States'),
                'need_identification_number':fields.boolean(
                                                'Need Identification Number'),
                'display_tax_label':fields.boolean('Display Tax Label'),
                'zone_id':fields.many2one('tr.presta.zone','Zone'),
                'currency_id':fields.many2one('res.currency','Currency'),
                'active':fields.boolean('Active'),
                }
    
    _defaults = {
                 'contains_states':lambda *a:False,
                 'need_identification_number':lambda *a:False,
                 'display_tax_label':lambda *a:False,
                 'active':lambda *a:True
                 }

Country()

class CountryState(osv.osv):
    
    _inherit = 'res.country.state'
    _prestashop = True
    _prestashop_name = 'states'
    
    _columns = {
                'active':fields.boolean('Active'),
                }
    
    _defaults = {
                 'active':lambda *a:True
                 }
    
    
CountryState()
