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
{
    "name": "OpenERP Prestashop Sync",
    "version": "1.0",
    "depends": ["base","product","sale","delivery","board","account_voucher"],
    "author": "Tech-Receptives Solutions Pvt. Ltd.",
    "website": 'http://www.techreceptives.com',
    "category": "E-commerce Syncronization",
    "description": """
            Synchronization with Prestashop E-commerce Store.
            Features are :
                1. Language Sync.
                2. Product Category Sync.
                3. Product Sync.
                4. Product Attribute Sync.
                5. Product Price Sync.
                6. Customer Sync.
                7. Order Sync.
                8. Tax Sync.
                And Much More ......
    """,
    "init_xml": [],
    'update_xml': [
                   'product/product_view.xml',
                   'product/tag/tag_view.xml',
                   'product/option/product_option_view.xml',
                   'sale/shop/sale_shop_view.xml',
                   'res/country_view.xml',
                   'res/currency_view.xml',
                   'res/language_view.xml',
                   'res/partner_view.xml',
                   'account/tax_view.xml',
                   "external_reference_view.xml",
                   "security/ir.model.access.csv",
                   'product/features/product_features_view.xml',
                   'delivery/delivery_view.xml',
                   'sale/sale_view.xml',
                    "image_sync/image_view.xml",
                    'product/wizard/view_product_wiz.xml',
                    "dashboard/board_sale_view.xml",
                    "menu_prestashop.xml",
                    "prestashop_installer_view.xml",
                   ],
    'demo_xml': [],
    'test' : [
              
            ],
    'installable': True,
    'active': False,
    'external_dependencies':{
        'python' : ['requests'],
  } 
}
