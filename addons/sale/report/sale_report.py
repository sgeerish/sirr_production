# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import tools
from osv import fields, osv
import convertion
class sale_report(osv.osv):
    _name = "sale.report"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'date': fields.date('Date Order', readonly=True),
        # 'date_confirm': fields.date('Date Confirm', readonly=True),
        # 'shipped': fields.boolean('Shipped', readonly=True),
        # 'shipped_qty_1': fields.integer('Shipped Qty', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        # 'uom_name': fields.char('Reference UoM', size=128, readonly=True),
        'product_uom_qty': fields.float('# of Qty', readonly=True),

        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True),
        # 'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True),
        'price_total': fields.float('Total Price', readonly=True),
        # 'delay': fields.float('Commitment Delay', digits=(16,2), readonly=True),
        'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
        'nbr': fields.integer('# of Lines', readonly=True),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], 'Order State', readonly=True),
    }
    _order = 'date desc'
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report')
        cr.execute("""
            create or replace view sale_report as (
                SELECT 
                  product_product.id AS product_id, 
                  sum(case when account_invoice.type in ('out_refund','sale_refund') then account_invoice_line.quantity * -1
                else account_invoice_line.quantity end) as product_uom_qty,  
                  account_invoice_line.price_subtotal AS price_total, 
                  res_users.name AS user_id, 
                  sale_shop.name AS shop_id, 
                  account_invoice.state AS state,
                  account_invoice.partner_id as partner_id,
                  account_invoice.type as type,
                  account_invoice.date_invoice as date,
                  product_template.uom_id as uom_id, 
		  product_template.categ_id as categ_id
                FROM 
                  public.account_invoice, 
                  public.account_invoice_line, 
                  public.product_product, 
                  public.product_template,
                  public.sale_shop, 
                  public.res_users
                WHERE 
                  account_invoice.user_id = res_users.id AND
                  account_invoice_line.invoice_id = account_invoice.id AND
                  account_invoice_line.product_id = product_product.id AND
                  res_users.shop = sale_shop.id AND
                  account_invoice.date_invoice>'2012-01-01' AND 
                  account_invoice.state not in ('cancel','draft')AND
		  product_product.product_tmpl_id = product_template.id AND
		  res_users.shop = sale_shop.id             
                GROUP BY
                  product_product.default_code,
                  product_product.name_template,
                  account_invoice_line.price_subtotal,
                  res_users.name,
                  sale_shop.name,
                  account_invoice.state,
                  account_invoice.type,
                  product_product.id,
                  account_invoice.partner_id,
                  account_invoice.date_invoice,
                  product_template.uom_id, 
		  product_template.categ_id
            )
        """)
sale_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
