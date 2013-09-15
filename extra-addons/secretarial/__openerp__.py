# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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


{
    'name': 'Company Secretary Management',
    'version': '0.1',
    'category': 'Custom',
    'author' : 'iSolve Web Solutions Ltd',
    'description': """
    This module provides features for a company's secretarial management.
    It gives you the possibility to
        * Manage Entities
        * Appoint Directors/Shareholders
        * Manage customer Accounts
        """,
    'depends': ['product','analytic','base','decimal_precision','board','crm'],
    'init_xml': [],
    'update_xml': [
		'wizard/shareholder_transfer_view.xml',
        'wizard/shareholder_transfer_view.xml',
        'company_secretary_view.xml',
        'secretarial_data.xml', 
      ],
    'demo_xml': ['board_company_secratary_demo.xml'],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
