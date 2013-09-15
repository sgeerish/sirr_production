# -*- encoding: utf-8 -*-
from osv import osv, fields,orm
import tools

class account_report_gl(osv.osv):
    _name="account.report.gl"
    _auto=False
    _columns={
        'date':fields.date('Date'),
        'partner_id':fields.many2one('res.partner','Partenaire'),
        'move_id':fields.many2one('account.move','Ecriture'),
        'account_id':fields.many2one('account.account','Compte'),
        'debit':fields.float('Debit'),
        'credit':fields.float('Credit'),
        'balance':fields.float('Balance'),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_report_gl')
        cr.execute("""
            CREATE OR REPLACE VIEW account_report_gl AS 
 SELECT min(account_move_line.move_id) AS id, account_move_line.date, account_move_line.partner_id, account_move_line.move_id, account_move_line.account_id, sum(account_move_line.debit) AS debit, sum(account_move_line.credit) AS credit, sum(account_move_line.debit - account_move_line.credit) AS balance
   FROM account_move_line
  WHERE account_move_line.date > '2012-09-01'::date AND account_move_line.date < '2012-09-29'::date
  GROUP BY account_move_line.account_id, account_move_line.partner_id, account_move_line.move_id, account_move_line.date
        """)    
    
account_report_gl()

class promotion_campagne(osv.osv):
    _name="promotion.campagne"
    _columns={
        'name':fields.char('Description',size=64),
        'pricelist_id':fields.many2one('product.pricelist','Liste de prix'),
        'product_promo':fields.one2many('product.promo', 'campagne_id', 'Promo'),
        'date_start':fields.date('Date debut'),
        'date_end':fields.date('Date fin'),
    }
promotion_campagne()

class product_promo(osv.osv):
    _name="product.promo"
    _columns={
        'name':fields.many2one('product.product','Produit'),
        'revient':fields.float('Revient'),
        'margin':fields.float('Marge'),
        'pv':fields.float('Prix de vente Actuel'),
        'proposition':fields.float('Proposition'),
        'new_margin':fields.float('Nouvelle Marge'),
        'campagne_id':fields.many2one('promotion.campagne','Campagne'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('name', False):
            if vals['name']:
                product=self.pool.get('product.product').browse(cr,uid,vals['name'])
                if vals['proposition']==0:
                    prop=1
                else:
                    prop=vals['proposition']
                vals.update({'revient': product.standard_price,
                            'margin':(product.lst_price-product.standard_price)/product.lst_price*100,
                            'pv':product.lst_price,
                            'new_margin':(vals['proposition']-product.standard_price)/prop*100})
        return super(product_promo, self).write(cr, uid, ids, vals, context=context)
    
product_promo()

class product_brand(osv.osv):
    _name = 'product.brand'
    _columns = {
        'name': fields.char('Brand Name',size=32),
        'description': fields.text('Description',translate=True),
        'logo_id' : fields.many2one('ir.attachment','Logo', help='Select picture file'),
        'partner_id' : fields.many2one('res.partner','partner', help='Select a partner for this brand if it exist'),
    }

product_brand()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'product_brand_id' : fields.many2one('product.brand','Brand', help='Select a brand for this product'),
        'supplier_ref':fields.char('Reference Flournisseur',size=64)
    }

product_product()

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'product_brand_id' : fields.many2one('product.brand','Brand', help='Select a brand for this product'),
        'supplier_ref':fields.char('Reference Flournisseur',size=64)
    }

product_template()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'garantie':fields.boolean('Garantie'),
        'vehicle':fields.char('Numero Vehicule',size=32),
        'client_id':fields.many2one('res.partner','Client'),
    }
purchase_order()