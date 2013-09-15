from osv import fields, osv
import time


class stock_compare_line(osv.osv):
    _name = "stock.compare.line"
    _description = "Stock Comparison Module Lines"
    def _get_diff(self, cr, uid, ids, name, arg, context=None):
        res={}
        for id in ids:
            # print id
            # print self.browse(cr,uid,id).new_qty-self.browse(cr,uid,id).old_qty
            res[id]=self.browse(cr,uid,id).new_qty-self.browse(cr,uid,id).old_qty
        return res
    _columns = {
        'name' : fields.many2one('product.product', 'Article'),
        'location_id' : fields.many2one('stock.location','Emplacement'),
        'old_qty': fields.float('Quantite Systeme'),
        'new_qty': fields.float('Quantite Physique'),
        'diff': fields.function(_get_diff, method=True, string='Ecart', type='float'),        
        'stock_compare_id':fields.many2one('stock.compare')
    }
    _order = 'name'
stock_compare_line()

class stock_compare(osv.osv):
    _name = "stock.compare"
    _description = "stock Comparison Module"
    
    _columns = {
        'name' : fields.char('Intitule', size=30),
        'date':fields.date('Date'),
        'product_id' : fields.one2many('product.product','stock_compare_id','Article'),
        'stock_line': fields.one2many('stock.compare.line', 'stock_compare_id', 'Stock Lines'),
        'state':fields.selection([
            ('draft', 'Brouillon'),
            ('done', 'Termine'),
            ('cancel', 'Cancelled')
            ], 'Etat', readonly=True)}
    _defaults = {
        'state': 'draft',
    }            
    def add_product(self, cr, uid, ids,context=None):
        obj_location=self.pool.get('stock.location')
        locations=obj_location.search(cr,uid,[('usage','=','internal')])
        product_obj_new = self.pool.get('product.product')    
        # print self
        compare=self.browse(cr,uid,ids)[0]
        stock_line_obj=self.pool.get('stock.compare.line')
        for product in compare.product_id:
            for l in obj_location.browse(cr,uid,locations):
                context['location']=l.id
                prod=product_obj_new.browse(cr, uid, product.id, context=context)
                if (prod.virtual_available<>0):
                    # print 'not zero',prod.virtual_available
                    # if(prod.virtual_available!=None):
                        # print  'virtual>0'
                        # print 'location',l
                        # print 'product',product
                        val = {
                        'name' : product.id,
                        'location_id' : l.id,
                        'old_qty': prod.virtual_available,
                        'new_qty': 0,
                        'stock_compare_id':compare.id
                        }                
                        stock_line_obj.create(cr,uid,val)
        return True
    def refresh_stock(self, cr, uid, ids,context=None):
        obj_location=self.pool.get('stock.location')
        # locations=obj_location.search(cr,uid,[('usage','=','internal')])
        product_obj_new = self.pool.get('product.product')    
        # print self
        compare=self.browse(cr,uid,ids)[0]
        stock_line_obj=self.pool.get('stock.compare.line')
        # stock_lines=stock_line.browse(cr,uid,ids)
        for stock_line in compare.stock_line:
            context['location']=stock_line.location_id.id
            prod=product_obj_new.browse(cr, uid, stock_line.name.id, context=context)
            if (prod.virtual_available<>0):
                # print 'not zero',prod.virtual_available
                # if(prod.virtual_available!=None):
                    # print  'virtual>0'
                    # print 'location',l
                    # print 'product',product              
                stock_line_obj.write(cr,uid,stock_line.id,{'old_qty':prod.virtual_available})
        return True        
        
    def confirm_stock(self,cr,uid,ids,context=None):
        obj_location=self.pool.get('stock.location')
        obj_product=self.pool.get('product.product')
        obj_stock_move=self.pool.get('stock.move')        
        for compare in self.browse(cr,uid,ids):
            for compare_line in compare.stock_line:
                if compare_line.new_qty>compare_line.old_qty:
                    move_qty=compare_line.new_qty-compare_line.old_qty
                    source=compare.x_dest_regul.id
                    destination=compare_line.location_id.id
                elif compare_line.new_qty<compare_line.old_qty:
                    move_qty=compare_line.old_qty-compare_line.new_qty
                    source=compare_line.location_id.id
                    destination=compare.x_dest_regul.id
                if compare_line.new_qty!=compare_line.old_qty:                    
                    val={
                        'name':compare_line.name.name,
                        'origin':'Sondage',
                        'location_id':source,
                        'location_dest_id':destination,
                        'product_id':compare_line.name.id,
                        'state':'confirmed',
                        'product_uom':compare_line.name.uom_id.id,
                        'product_qty':move_qty
                    }
                    obj_stock_move.create(cr,uid,val)
                if not compare_line.name.sondage:
                    obj_product.write(cr,uid,compare_line.name.id,{'sondage':True})
            for prod_line in compare.product_id:
                obj_product.write(cr,uid,prod_line.id,{'sondage':True})
        self.write(cr,uid,ids,{'state':'done'})
        return True
    def update_price(self,cr,uid,ids,context=None):
        obj_product=self.pool.get('product.product')
        for compare in self.browse(cr,uid,ids):
            for prod_line in compare.product_id:
                price=prod_line.lst_price
                if compare.x_type=='perc':
                    new_price=price+(price*compare.x_value/100)
                else:
                    new_price=price+compare.x_value
                obj_product.write(cr,uid,prod_line.id,{'list_price':new_price})
        self.write(cr,uid,ids,{'state':'done'})
        return True
        
    def cancel_stock(self,cr,uid,ids,context=None):
        obj_location=self.pool.get('stock.location')
        obj_product=self.pool.get('product.product')
        obj_stock_move=self.pool.get('stock.move')        
        for compare in self.browse(cr,uid,ids):
            for compare_line in compare.stock_line:
                if compare_line.new_qty>compare_line.old_qty:
                    move_qty=compare_line.new_qty-compare_line.old_qty
                    destination=compare.x_dest_regul.id
                    source=compare_line.location_id.id
                elif compare_line.new_qty<compare_line.old_qty:
                    move_qty=compare_line.old_qty-compare_line.new_qty
                    destination=compare_line.location_id.id
                    source=compare.x_dest_regul.id
                if compare_line.new_qty!=compare_line.old_qty:                    
                    val={
                        'name':compare_line.name.name,
                        'origin':'Sondage Annulation',
                        'location_id':source,
                        'location_dest_id':destination,
                        'product_id':compare_line.name.id,
                        'state':'confirmed',
                        'product_uom':compare_line.name.uom_id.id,
                        'product_qty':move_qty
                    }
                    obj_stock_move.create(cr,uid,val)
                if not compare_line.name.sondage:
                    obj_product.write(cr,uid,compare_line.name.id,{'sondage':False})
        self.write(cr,uid,ids,{'state':'cancel'})
        return True        
        
stock_compare()

class product_product(osv.osv):
    _inherit="product.product"
    _columns = {
        'sondage':fields.boolean('Sondage'),
        'stock_compare_id':fields.many2one('stock.compare'),
    }
product_product()
