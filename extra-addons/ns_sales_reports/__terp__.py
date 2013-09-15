# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2003-2010 NS-Team (<http://www.ns-team.fr>). All Rights Reserved
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
    "name" : "ns_sales_reports",
    "version" : "1.2",
    "description": "Sales Reports using Jasper Reports",
    "author" : "NS-Team",
    'website': 'http://www.ns-team.fr',
    "category" : "Custom",
    "depends" : ["account","product","sale","jasper_reports"],
    "init_xml" : [],
    "demo_xml" : [],
    'update_xml': ["ns_sales_reports.xml","ns_sales_reports_wizard.xml"],
    'installable': True,
    'active': False,
}
