from osv import fields, osv
import time
import datetime
from datetime import datetime
import tools

class socolait_discount(osv.osv):
    _name = "socolait.discount"
    _description = "Discount information"
    _columns = {
        'name': fields.char('Libele', size=60, required=True),
        'date_start': fields.date('Date Debut', required=True),
        'date_end': fields.date('Date Fin', required=True),
        'discount': fields.float('Remise', digits=(12,10),required=True),
        'product_id': fields.many2one('product.product','Produit'),
        'partner_ids': fields.one2many('res.partner','discount_id','Clients'),        
    }    
socolait_discount()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'discount_id': fields.many2one('socolait.discount', 'Discount'),
    }
res_partner()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context=None):
        result =  super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name, partner_id,
                        lang, update_tax, date_order, packaging, fiscal_position, flag)
        discount_object=self.pool.get('socolait.discount')
        disc_ids=discount_object.search(cr,uid,[('date_end','>=',date_order),('date_start','<=',date_order)])
        discount=0
        print 'dateorder',date_order
        print 'discids',disc_ids
        for disc_line in discount_object.browse(cr,uid,disc_ids):
            print 'product',product
            print 'disc prod',disc_line.product_id
            if disc_line.product_id.id==product:
                if not disc_line.partner_ids:
                    print 'no partners'
                    discount=line.discount
                else:
                    print 'partners found'
                    for customer in disc_line.partner_ids:
                        print customer,partner_id
                        if customer.id==partner_id:
                            discount=disc_line.discount
        result['value']['discount'] = discount
        print discount
        return result
sale_order_line()
