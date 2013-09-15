from osv import fields, osv
import time

class stock_vehicle(osv.osv):
    _name = "stock.vehicle"
    _description = 'Vehicules'
    _columns = {
        'name' : fields.char('Immatriculation',size=32),
        'date_controle' : fields.date('Controle technique'),
        'fuel_type': fields.selection([('diesel','Gasoil'),('fuel','Essence')],'Carburant'),
        'date_circulation': fields.date('Date Circulation'),
        'date_fin_assurance': fields.date('Fin Assurance'),
    }
    _order = 'name'
stock_vehicle()

class stock_driver(osv.osv):
    _name = "stock.driver"
    _description = 'Drivers'
    _columns = {
        'name' : fields.char('Nom',size=64),
    }
    _order = 'name'
stock_driver()

class stock_picking(osv.osv):
    _inherit="stock.picking"
    _columns = {
        'vehicle_id':fields.many2one('stock.vehicle','Vehicule'),
        'driver_id':fields.many2one('stock.driver','Chauffeur'),
        'date_livraison': fields.date('Date Livraison'),        
        'order_amount':fields.related('sale_id', 'amount_total', type="float", string="Montant", store=False),
        'order_divers_name':fields.related('sale_id', 'name_divers', type="char", string="Nom Divers", store=False),
        'order_divers_address':fields.related('sale_id', 'address_divers', type="char", string="address Divers", store=False),
    }
stock_picking()

class delivery_parameter(osv.osv):
    _name="delivery.parameter"
    _columns = {
        'name':fields.char('Description',size=32),
        'limit_tariff':fields.float('Limite Tarifaire'),
        'limit_free':fields.float('Limite Gratuit'),
        'delivery_product_id_free':fields.many2one('product.product','Reference Livraison Gratuite'),
        'chargeable_partner_ids':fields.one2many('res.partner','chargeable_id','Payable'),
        'free_partner_ids':fields.one2many('res.partner','free_id','Gratuit'),
        'special_products':fields.one2many('product.product','special_product_id','Special'),
    }
delivery_parameter()

class product_product(osv.osv):
    _inherit="product.product"
    _columns = {
        'special_product_id':fields.many2one('delivery.parameter','Produit Speciale'),
    }
product_product()



class res_partner(osv.osv):
    _inherit="res.partner"
    _columns = {
        'free_id':fields.many2one('delivery.parameter','Livraison Gratuite'),
        'chargeable_id':fields.many2one('delivery.parameter','Livraison Payante'),
        
    }
res_partner()

class delivery_zone(osv.osv):
    _name="delivery.zone"
    _columns = {
        'name':fields.char('Quantier',size=64),
        'limit1':fields.many2one('product.product','Reference Livraison Limite 1'),
        'limit2':fields.many2one('product.product','Reference Livraison Limite 2'),        
    }
delivery_zone()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'delivery_product':fields.boolean('Produit Livraison'),
        'delivery_zone':fields.many2one('delivery.zone','Quartier'),
        'delivery_product_id':fields.many2one('product.product','Produit Livraison'),
        'delivery_amount':fields.float('Montant Livraison'),
    }
    def get_delivery_product(self, cr, uid, ids, context=None):
        del_param_obj=self.pool.get('delivery.parameter')
        zone_obj=self.pool.get('delivery.pool')
        sol=self.pool.get('sale.order.line')
        param_ids=del_param_obj.search(cr,uid,[])
        so_obj=self.pool.get('sale.order')
        params=del_param_obj.browse(cr,uid,param_ids)[0]
        products=[]
        for so in so_obj.browse(cr,uid,[ids]):
            amount_total=0
            if not so.delivery_product:
                for sl in so.order_line:
                    if sl.x_livraison=='livraison':
                        amount_total+=sl.price_subtotal
                        products.append(sl.product_id.id)
                if products in params.special_products:
                    if amount_total<limit_free:
                        zone=zone_obj.browse(cr,uid,so.zone_id.id)[0]                
                        if amount_total<limit_tariff:
                            delivery_product=zone.limi1
                        else:
                            delivery_product=zone.limi2
                    else:
                        delivery_product=params.delivery_product_id_free
                else:
                    if so.partner_id.id in params.chargeable_partner_ids:
                        if amount_total<limit_free:
                            zone=zone_obj.browse(cr,uid,so.zone_id.id)[0]                
                            if amount_total<limit_tariff:
                                delivery_product=zone.limi1
                            else:
                                delivery_product=zone.limi2
                        else:
                            delivery_product=params.delivery_product_id_free
                    else:
                        delivery_product=params.delivery_product_id_free
                so_obj.write(cr,uid,[so.id],{'delivery_product' : delivery_product.id,'delivery_amount':delivery_product.lst_price,'delivery_product':True})                        
        return True
sale_order()
