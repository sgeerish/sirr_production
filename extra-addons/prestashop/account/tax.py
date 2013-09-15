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

class tax_rule_group(osv.osv):
    _name = 'tax.rule.group'
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'tax_rule_groups'
    
    _columns = {
                'name':fields.char('Name',size=64, 
                                   help="Name for tax rule groups."),
                }
                                                                  
tax_rule_group()

class tax_rules(osv.osv):
    
    _name = 'tax.rules'
    _prestashop = True
    _prestashop_name = 'tax_rules'
    
    _columns = {
                'tax_id':fields.many2one('account.tax','Tax'),
                'tax_rule_group_id':fields.many2one('tax.rule.group',
                                   'Tax Rule Group',
                                    help="Fetch name for tax rule groups"),
                'state_id':fields.many2one('res.country.state','State', 
                                    help="Full name of state"),
                'country_id':fields.many2one('res.country','Country', 
                                    help="Full name of country"),
                'state_behavior':fields.boolean('State Behavior'),
                }
    
tax_rules()

class account_tax(osv.osv):
    
    _inherit = 'account.tax'
    _prestashop = True
    _not_thread = True
    _prestashop_name = 'taxes'
    
    _columns = {

                'delete':fields.boolean('delete'),
                }
    
account_tax()
