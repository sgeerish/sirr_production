# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
    "name" : "Purchase Shipping tracking",
    "version" : "1.0",
    "author" : "Open Mind Ltd",
    "website": "www.isolve-web.com",
    "license" : "GPL-3",
    "category" : 'Generic Modules/Sales & Purchases',
    "description": """Add shipment tracking on Purchases
""",
    "depends" : [
        "purchase",
        ],
    "data": [
        "security/purchase_shipping_security.xml",
        "security/ir.model.access.csv"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "active": False,
    "installable": True
}
