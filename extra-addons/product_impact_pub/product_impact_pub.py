from osv import fields, osv
import datetime
from datetime import date
from mx import DateTime
import time
import ir
import netsvc

class pub_category(osv.osv):
    _name="pub.category"
    _description = " "
    _columns = {
        'name':fields.char('Categorie', size=30),
    }
pub_category()

class publication(osv.osv):
    _name="publication"
    _columns = {
        'date':fields.date('Date'),
        'type':fields.many2one('pub.category','Type'),
        'name':fields.char('Name',size=30),
        'amount':fields.float('Montant'),
        'pub_id':fields.many2one('pub.analysis'),
        
    }
publication()

class pub_analysis(osv.osv):
    _name="pub.analysis"
    
    _columns ={
    'date_debut':fields.date('Date debut'),
    'date_fin':fields.date('Date fin'),
    'name':fields.char('Campagne Pub',size=30),
    'product_id' : fields.one2many('product.product','pub_id','Article'),
    'product_line':fields.one2many('product.line','pub_id'),
    'publication_line':fields.one2many('publication','pub_id'),
    'amount':fields.float('Montant'),
    }
    def get_sales_lines(self,cr,uid,ids,contaxt=None):
        
        product_obj=self.pool.get('product.product')
        invoice_line=self.pool.get('account.invoice.line')
        invoice_obj=self.pool.get('account.invoice')
        for sl in self.browse(cr, uid, ids):
            prods = []
            date_fin=DateTime.strptime(sl.date_fin, '%Y-%m-%d')
            date_debut=DateTime.strptime(sl.date_debut, '%Y-%m-%d')            
            for p in sl.product_id:
                prods.append(p.id)
            prods=tuple(prods)
            invoice_ids=invoice_obj.search(cr,uid,[('date_invoice','>=',date_debut),('date_invoice','<=',date_fin),('type','in',['out_invoice','out_refund'])])
            invoice_lines=invoice_line.search(cr,uid,[('invoice_id','in',invoice_ids),('product_id','in',prods)])
            
            invoice_lines=invoice_line.browse(cr,uid,invoice_lines)
            stock_line_obj=self.pool.get('product.line')                   
            for line in invoice_lines:
                prod=product_obj.browse(cr, uid, line.product_id.id)
                val = {
                    'date':line.invoice_id.date_invoice,
                    'quantite':line.quantity,
                    'name' : line.product_id.id,
                    'sale_price':line.price_unit,
                    'amount':line.price_subtotal,
                    'cost':line.product_id.standard_price*line.quantity,
                    'cost_unit':line.product_id.standard_price,
                    'virtual_quantity':prod.virtual_available,
                    'pub_id':sl.id
                }
                
        # print self
                stock_line_obj.create(cr,uid,val)
        return True
pub_analysis()
    
class product_line(osv.osv):
    _name = "product.line"
    _description = "analyse pub"

    _columns = {
        'date':fields.date('Date'),
        'quantite':fields.float('Quantite'),
        'name' : fields.many2one('product.product', 'Article'),
        'sale_price':fields.float('PV HT'),
        'amount':fields.float('PVT HT'),
        'cost':fields.float('PRT'),
        'cost_unit':fields.float('PR'),
        'pub_id':fields.many2one('pub.analysis'),
        'virtual_quantity':fields.float('Qte Dispo'),
        
    }
product_line()

class product_product(osv.osv):
    _inherit="product.product"

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        warehouse_obj=self.pool.get('stock.warehouse')
        warehouses=warehouse_obj.search(cr,uid,[])
        depot1=warehouses[0]
        depot2=warehouses[1]
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'qty_available':
                c.update({ 'states': ('done',), 'what': ('in', 'out') })
            if f == 'virtual_available':
                c.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out') })
            if f == 'incoming_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('in',) })
            if f == 'outgoing_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('out',) })
            if f == 'stock_depot1':
                c.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out'),'warehouse':depot1 })
            if f == 'stock_depot2':
                c.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out'),'warehouse':depot2 })

            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        return res

    _columns = {
        'pub_id':fields.many2one('pub.analysis'),
        'stock_depot1': fields.function(_product_available, method=True, type='float', string='Depot 1', multi='qty_available'),
        'stock_depot2': fields.function(_product_available, method=True, type='float', string='Depot 2', multi='qty_available'),

    }
product_product()


class mrp_production_confirm(osv.osv_memory):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "mrp.production.confirm"
    _description = "Confirmer les Ordres de Fabrication"

    def mrp_production_confirm(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        data_inv = pool_obj.get('mrp.production').read(cr, uid, context['active_ids'], ['state'], context=context)

        for record in data_inv:
            if record['state']!= 'draft':
                raise osv.except_osv(_('Warning'), _("Validation Impossible!"))
            wf_service.trg_validate(uid, 'mrp.production', record['id'], 'button_confirm', cr)
        return {'type': 'ir.actions.act_window_close'}

mrp_production_confirm()


