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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import convertion
from osv import fields, osv
import netsvc
from tools.translate import _
from tools.translate import _
import ir
import netsvc


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def get_shop(self, cr, uid, ids):
        user=self.pool.get('res.users').browse(cr,uid,uid)
        if user.shop.name=='Importation':
            return user.shop.name
        else:
            return 'Locaux'
    
    _columns = {
        'order_line': fields.one2many('purchase.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)],'start': [('readonly', False)]}),
        'create':fields.many2one('res.users', 'Demandeur'),
        'daf':fields.many2one('res.users', 'Direction Financiere'),
        'dg':fields.many2one('res.users', 'Direction Generale'),
        'sb':fields.many2one('res.users', 'Direction Commerciale'),
        'date_daf':fields.date('Date Appr. DAF'),
        'date_dg':fields.date('Date Appr. DG'),
        'date_sb':fields.date('Date Appr. SB'),
        'ref':fields.char('Reference Commande', size=64),
        'cur_rate':fields.float('Cours Devise'),
        'containers':fields.float('Conteneurs'),
        'estimated_freight':fields.float('Meilleur taux de fret Estimatif'),
        'incoterm':fields.many2one('stock.incoterms', 'Incoterm'),
        'product_origin':fields.many2one('res.country', 'Origine'),
        'shop_id': fields.many2one('sale.shop', 'Souche', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'payment_term': fields.many2one('account.payment.term', 'Condition de Reglement'),
    }
    
    
    def price_approve(self, cr, uid, ids,
            name=None, args=None, context=None):
        "Return the total quantity in an invoice"
        inv_line_obj = self.pool.get('purchase.order.line')
        prod=self.pool.get('product.product')
        inv_obj = self.browse(cr,uid,ids)
        for lines in inv_obj:
            for line in lines.order_line:
                if not line.product_id:
                    continue
                prod_id=line.product_id.id
                #if line.product_id.standard_price==0:
                prod.write(cr,uid,prod_id,{'standard_price':line.x_new_cost})
                prod.write(cr,uid,prod_id,{'list_price':line.x_new_sale_price})
        return True
    
    
    def onchange_partner_id(self, cr, uid, ids, part):

        if not part:
            return {'value':{'partner_address_id': False, 'fiscal_position': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['default'])
        part = self.pool.get('res.partner').browse(cr, uid, part)
        pricelist = part.property_product_pricelist_purchase.id
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        return {'value':{'partner_address_id': addr['default'], 'pricelist_id': pricelist, 'fiscal_position': fiscal_position,'payment_term':payment_term}}
    
    _defaults = {
        'create': lambda obj, cr, uid, context: uid,
        #'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, obj.get_shop(cr,uid,obj)),
    }
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'nomenclature': fields.related('product_id','nomenclature', type='many2one', relation='product.nomenclature', string='Nomenclature'),
    }
    def onchange_discount_purchase(self,cr,uid,ids,disc,unit_price):
        res={}
        return {'value':{'x_unit_discount': (unit_price*((100-disc)/100)) }}
purchase_order_line()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'create':fields.many2one('res.users', 'Vendeur'),
        'validate':fields.many2one('res.users', 'Dir. Com.'),
        'date_create':fields.date('Date Creation'),
        'date_validate':fields.date('Date Appr. DC'),
        'name_divers':fields.char('Nom Occasionel', size=64),
        'tel_divers':fields.char('Telephone Occasionel', size=64),
        'address_divers':fields.char('Addresse Occasionel', size=64),
        'cheque':fields.boolean('Paiement Cheque?')
    }
    
    _defaults = {
        'create': lambda obj, cr, uid, context: uid,
    }

    def create_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        sale_obj = self.browse(cr,uid,ids)
        
        for order in self.browse(cr, uid, ids, context={}):
            proc_ids = []
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            picking_id = False
            for line in order.order_line:
                date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)

                move_id = False
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    location_id = order.shop_id.warehouse_id.lot_stock_id.id
                    if line.location:
                        location_id=line.location.id
                        
                    newdate = data_planned
                    produce_id = production_obj.create(cr, uid, {
                        'origin': sale_obj.name,
                        'x_partner_id':sale_obj.partner_id.id,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'th_weight':line.th_weight,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'location_src_id': False,
                        'location_dest_id': line.x_enlevement.x_finished.id,
                        'bom_id': False,
                        'company_id': procurement.company_id.id,
                    })
                    
                    if not picking_id:
                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'name': pick_name,
                            'origin': 'PROD' + order.name,
                            'type': 'out',
                            'state': 'manual',
                            'move_type': order.picking_policy,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': 'none',
                            'company_id': order.company_id.id,
                        })                        
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': line.name[:64],
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'date': date_planned,
                        'date_expected': date_planned,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos_qty,
                        'product_uos': (line.product_uos and line.product_uos.id)\
                                or line.product_uom.id,
                        'product_packaging': line.product_packaging.id,
                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'location_id': line.x_enlevement.x_finished.id,
                        'location_dest_id': line.x_enlevement.x_route.id,
                        'tracking_id': False,
                        'state': 'draft',
                        'note': line.notes,
                        'company_id': order.company_id.id,
                    })

        return True
    
    
sale_order()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _columns = {
        'th_weight':fields.float('M. Lineare'),
    }
procurement_order()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
        'th_weight':fields.float('M. Lineare'),
    }
mrp_production()


class excel_reports(osv.osv):
    _name = 'excel.reports'
    _description ='Excel Reports'
    _columns = {
        'name':fields.char('Description',size=64),
        'report':fields.binary('Rapport'),

    }
excel_reports()


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'location':fields.many2one('stock.location', 'Emplacement'),
    }
    def getlocation(self, cr, uid, ids, loc):
        res={}
        cur_user=self.pool.get('res.users').browse(cr,uid,uid)
        shop=cur_user.shop.name
        shop='%'+shop+'%'
        current_loc=loc
        locations=self.pool.get('stock.location').search(cr,uid,[('location_id.name','like',shop)])
        if current_loc in locations:
            return {'value':{'location': loc}}
        else:
            for id in ids:
                return {'value':{'location': locations[0]}}
        return {'value':{'location': locations[0]}}
    def product_discount_change(self, cr, uid, ids, discount,max):
        warning={}
        if discount>max:
            warning = {
                    'title': _('Remise incorrect !'),
                    'message': _('Remise Maximum atteint!!!') 
            }
        user_obj=self.pool.get('res.users')
        user=user_obj.browse(cr,uid,uid)
        if user.x_discount:
            if user.x_discount>0:
                max=user.x_discount
        discount=min(discount,max)   
        return {'value':{'discount': discount},'warning':warning}
        
    def onchange_price_unit(self, cr, uid, ids, pricelist,product,qty,uom,partner_id,date_order,price_unit):
        warning={}
        price=price_unit
        if product:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom,
                    'date': date_order,
                    })[pricelist]
        
        if price is False:
            warning = {
                'title': 'No valid pricelist line found !',
                'message':
                    "Couldn't find a pricelist line matching this product and quantity.\n"
                    "You have to change either the product, the quantity or the pricelist."
                }
        if price_unit<price:
            warning = {
                    'title': _('Prix incorrect !'),
                    'message': _('Peux pas dimunuer les prix atteint!!!') 
            }
        prix=max(price,price_unit)   
        if product:
            return {'value':{'price_unit': prix},'warning':warning}
        else:
            pass
            
sale_order_line()


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    def change_cheque_account(self,cr,uid,ids,journal_id):
        # print 'Checking'
        voucher=self.pool.get('account.voucher')
        move=self.pool.get('account.move.line')
        journal=self.pool.get('account.journal')
        journal=journal.browse(cr,uid,journal_id)
        voucher_line=self.pool.get('account.voucher.line')
        res={}
        for line in self.browse(cr, uid, ids):
            for move_line in line.move_ids:
                if journal.x_temporary_account and move_line.account_id==journal.default_credit_account_id:
                    print 'writing...'
                    print move_line.id  
                    print move_line.account_id
                    print journal.x_temporary_account.id
                    recs = []
                    recs += [move_line.id]
                    state=move_line.state
                    # move.write(cr,uid,recs,{'state':'draft'})
                    sql="UPDATE account_move_line set account_id=%d where id=%d" % (journal.x_temporary_account.id,move_line.id)
                    cr.execute(sql)
                    res2 = cr.commit()                    
                    # move.write(cr,uid,recs,{'account_id':journal.x_temporary_account.id,'state':state})
                    return{'value':res} 
        return{'value':res} 
        
    def onchange_bank_date(self,cr,uid,ids,date):
        res={}
        for line in self.browse(cr, uid, ids):
            ds = datetime.strptime(line.date, '%Y-%m-%d')
            if date<ds:
                return{'value':{'banking_date':ds}}
        return {}
        
    def button_cheque_account(self,cr,uid,ids,context=None):
        print 'clicked'
        voucher=self.pool.get('account.voucher')
        move=self.pool.get('account.move.line')
        journal=self.pool.get('account.journal')
        voucher_line=self.pool.get('account.voucher.line')
        res={}
        for line in self.browse(cr, uid, ids):
            journal_id=line.journal_id.id
            journal=journal.browse(cr,uid,journal_id)
            for move_line in line.move_ids:
                print move_line
                print move_line.id
                if journal.x_temporary_account and move_line.account_id==journal.default_credit_account_id:
                    sql="UPDATE account_move_line set account_id=%d where id=%d" % (journal.x_temporary_account.id,move_line.id)
                    cr.execute(sql)
                    res2 = cr.commit()     
                    return True
        return True       
    def change_cheque_return(self,cr,uid,ids,journal_id):
        voucher=self.pool.get('account.voucher')
        move=self.pool.get('account.move.line')
        journal=self.pool.get('account.journal')
        journal=journal.browse(cr,uid,journal_id)
        voucher_line=self.pool.get('account.voucher.line')
        cheque_return=self.pool.get('cheque.return')
        li=self.browse(cr,uid,ids)[0]
        val = {
            'paiement':li.id,
            'cheque':li.reference,
            'amount':li.amount,
            'partner_id':li.partner_id.id
                }
        cheque_return.create(cr,uid,val)
        res={}
        for line in self.browse(cr, uid, ids):
            for move_line in line.move_ids:
                if journal.x_temporary_account and move_line.account_id==journal.x_temporary_account:
                    sql="UPDATE account_move_line set account_id=%d where id=%d" % (journal.default_credit_account_id.id,move_line.id)
                    cr.execute(sql)
                    res2 = cr.commit()   
                    return{'value':res}         
        return{'value':res}         
    def move_line_id_payment_get(self, cr, uid, ids, *args):
        if not ids: return []
        result = self.move_line_id_payment_gets(cr, uid, ids, *args)
        return result.get(ids[0], [])

    def move_line_id_payment_gets(self, cr, uid, ids, *args):
        res = {}
        if not ids: return res
        cr.execute('SELECT i.id, l.id '\
                   'FROM account_move_line l '\
                   'LEFT JOIN account_voucher i ON (i.move_id=l.move_id) '\
                   'WHERE i.id IN %s '\
                   'AND l.account_id=i.account_id',
                   (tuple(ids),))
        for r in cr.fetchall():
            res.setdefault(r[0], [])
            res[r[0]].append( r[1] )
        return res
    def _get_invoice_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return invoice_ids
        
    def test_paid(self, cr, uid, ids, *args):
        res = self.move_line_id_payment_get(cr, uid, ids)
        # print res
        if not res:
            return False
        ok = True
        for id in res:
            cr.execute('select reconcile_id from account_move_line where id=%s', (id,))
            ok = ok and  bool(cr.fetchone()[0])
        return ok
    
    #def _reconciled(self, cr, uid, ids, name, args, context=None):
    #    res = {}
    #    for id in ids:
    #        res[id] = self.test_paid(cr, uid, [id])
    #    return res
    
    def _reconciled(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context={}
        result = {}
        for order in self.browse(cr,uid,ids, context=context):
            result[order.id]=False
            if order.move_ids != []:
                for move_id in order.move_ids:
                    if move_id.account_id == order.journal_id.default_credit_account_id or move_id.account_id==order.journal_id.x_temporary_account:
                        if not move_id.reconcile_id:
                            result[order.id]=False
                        else:
                            result[order.id] = True
                            self.write(cr,uid,order.id,{'check_return':False})
        return result
    
    def deposit_check(self, cr, uid, ids, context=None):             
        self.write(cr, uid, ids, {'state':'check_deposit'})
        return True
        
    def confirm_deposit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'check_bank'})
        return True

    def action_cancel_check(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'check_return'})
        return True
    def action_check_escompte(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'journal_id':'ESC'})
        self.write(cr, uid, ids, {'account_id':'511400'})
        return True

    _columns = {
        'instrument_type':fields.char('Type', size=64),
        'instrument_date':fields.date('Date'),
        'transmitted':fields.date('Transmis'),
        'to_account':fields.date('Compta'),
        'ref': fields.related('partner_id','ref', type='char', relation='res.partner', string='Code', readonly=1),
        'reconciled': fields.function(_reconciled, method=True,string='Reconciled', type='boolean'),
        'instrument_bank':fields.many2one('res.bank','Banque'),
        'banking_date':fields.date('Mise En Banque'),
        'banking_bank':fields.many2one('res.bank','Banque'),
        'banking_number':fields.char('N° bordereau', size=64),
        'check_return':fields.boolean('Retourné'),
        'balance':fields.float('Balance'),
        'tire':fields.char('Tire', size=64),
        'state':fields.selection(
            [('draft','Draft'),
             ('proforma','Pro-forma'),
             ('check_deposit','En Reglement'),
             ('check_return','Reglement Retourné'),
             ('check_bank','Reglement deposée en banque'),
             ('posted','Posted'),
             ('cancel','Cancel')], 'State', readonly=True, size=32,),
        }       
    
    def onchange_bank(self, cr, uid, ids, move_ids,bank):
        move_lines=self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids):
            recs = []
            for line in voucher.move_ids:
                recs += [line.id]
        move_lines.write(cr, uid, recs,{'bank':bank})
        return True
    def onchange_check_bal(self,cr,uid,ids,partner_id,amount):
        voucher=self.pool.get('account.voucher')
        voucher_line=self.pool.get('account.voucher.line')
        res={}
        total_cr=0
        total_dr=0
        balance=0
        default = {
            'value':{'x_payment_balance':0},
        }
        payment=amount
        transaction=0
        if not partner_id:
            return default
        else:
            for voucher_id in self.browse(cr,uid,ids):
                print 'entering voucher'
                for v in voucher_id.line_cr_ids:
                    if v.amount!=0:
                        total_cr+=v.amount
                for v in voucher_id.line_dr_ids:
                    if v.amount!=0:
                        total_dr+=v.amount
                transaction=total_cr-total_dr
                print transaction
        balance=payment-transaction
        res['x_payment_balance']=balance
#        self.write(cr,uid,ids,{'x_payment_balance':balance})
        default['value']={'x_payment_balance':balance}
        # print default
        return default
        #return True
                
    def check_bal(self,cr,uid,ids,context=None):
        voucher=self.pool.get('account.voucher')
        voucher_line=self.pool.get('account.voucher.line')
        res={}
        total_cr=0
        total_dr=0
        for voucher_id in self.browse(cr,uid,ids):
            print 'Entering'
            payment=voucher_id.amount
            for v in voucher_id.line_cr_ids:
                if v.amount!=0:
                    total_cr+=v.amount
            for v in voucher_id.line_dr_ids:
                if v.amount!=0:
                    total_dr+=v.amount
            transaction=total_cr-total_dr
            balance=payment-transaction
            if balance!=0:
                warn_msg = _("Montant Paye.\t\t:%s\n"
                "Montant Transactions.:%s\n"
                "Balance\t\t\t\t:%s\n") % \
                    (payment,transaction,balance)
                warning = {
                    'title': _('Balance !'),
                    'message': warn_msg
                    }
#	res['x_payment_balance']=balance 
        print 'out'
        self.write(cr,uid,ids,{'x_payment_balance':balance})
#        return {'value':res}
        return True                
account_voucher()

class account_voucher_line(osv.osv):
    _inherit='account.voucher.line'
    def onchange_move_line_id(self, cr, user, ids, move_line_id,reference,amount,context=None):
        """
        Returns a dict that contains new values and context

        @param move_line_id: latest value from user input for field move_line_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        res = {}
        instrument=reference
        voucher_line=self.pool.get('account.voucher.line')
        print 'entering smtp_custom_account_voucher'
        move_line_pool = self.pool.get('account.move.line')
        if move_line_id:
            move_line = move_line_pool.browse(cr, user, move_line_id, context=context)
            if move_line.credit:
                ttype = 'dr'
            else:
                ttype = 'cr'
                
            account_id = move_line.account_id.id
            res.update({
                'account_id':account_id,
                'type': ttype, 
            })
        return {
            'value':res,
        } 

    def onchange_payment_amount(self,cr,uid,ids,amount,old_amount,payment):
        voucher=self.pool.get('account.voucher')
        voucher_line=self.pool.get('account.voucher.line')
        res={}
        for line in self.browse(cr, uid, ids):
            voucher_id=line.voucher_id
            current_voucher=voucher.browse(cr,uid,voucher_id)
            voucher_amount=current_voucher.amount
            total_receipts=0
            total_payments=0
            debit_line_amounts=0
            credit_line_amounts=0            
            if amount>line.amount_unreconciled:
                proposed_amount=line.amount_unreconciled
                res['amount']=line.amount_unreconciled
                res['x_old_amount']=res['amount']
            else:
                res['amount']=amount
                res['x_old_amount']=amount
        return{'value':res} 
        
     
account_voucher_line()


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    def get_po_qty(self,cr,uid,id,product):
        bc=self.x_po.order_line.search(cr,uid,[('product_id','=',product)])
        return bc[0].product_qty
    
    def action_invoice_ship_create(self, cr, uid, ids, *args):
        wf_service = netsvc.LocalService("workflow")
        picking_id = False
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids, context={}):
            if order.type=='out_invoice' and not order.x_so and not order.origin:
                proc_ids = []
                output_id = self.pool.get('res.users').browse(cr, uid, uid).shop.warehouse_id.lot_output_id.id
                location_id = self.pool.get('res.users').browse(cr, uid, uid).location.id
                picking_id = False
                for line in order.invoice_line:
                    proc_id = False
                    date_planned = datetime.now() + relativedelta(0.0)
                    date_planned= date_planned.strftime('%Y-%m-%d %H:%M:%S')
                    move_id = False
                    if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                        if not picking_id:
                            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
                            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                'name': pick_name,
                                'origin': order.number,
                                'type': 'out',
                                'state': 'auto',
                                'move_type': 'direct',
                                'address_id': order.address_invoice_id.id,
                                'invoice_state': 'none',
                                'company_id': order.company_id.id,
                            })
                        move_id = self.pool.get('stock.move').create(cr, uid, {
                            'name': line.name[:64],
                            'discount':line.discount,
                            'picking_id': picking_id,
                            'product_id': line.product_id.id,
                            'date': date_planned,
                            'date_expected': date_planned,
                            'product_qty': line.quantity,
                            'product_uom': line.uos_id.id,
                            'product_uos_qty': line.quantity,
                            'product_uos': line.uos_id.id,
                            'address_id': order.address_invoice_id.id,
                            'location_id': line.location.id or location_id,
                            'location_dest_id': output_id,
                            'tracking_id': False,
                            'state': 'draft',
                            #'state': 'waiting',
                            'company_id': order.company_id.id,
                        })

                        proc_ids.append(proc_id)

                val = {}

                if picking_id:
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

                #for proc_id in proc_ids:
                #    wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

                val['shipped'] = False

                self.write(cr, uid, [order.id], val)
        return True


    def get_move_qty(self,cr,uid,id,product):
	bc=self.x_picking_id.move_lines.search(cr,uid,[('product_id','=',product)])
	return bc[0].product_qty

    def check_printed(self,cr,uid,id):
        if self.printed:
            return True
        else:
            sql="UPDATE account_invoice set printed=True where id=%d" % (id)
            self.cr.execute(sql)
            res = self.cr.commit()
            # print '>>>>>>>>>>>>>>>>>>'
            return False
    
    def _check_paid(self, cr, uid, ids, name, args, context=None):
        res={}
        voucher_lines=self.pool.get('account.voucher.line')
        res[id]=True
        return res

    def test_check(self, cr, uid, ids, *args):
        ok = False
        voucher_lines=self.pool.get('account.voucher.line')
        for line in self.browse(cr, uid, ids):
            res=voucher_lines.search(cr, uid, [('name', 'like', line.number), ('instrument_number', '!=', '')])
            if res:
                ok= True
            else:
                ok= False
        return ok
    def test_allowed(self, cr, uid, ids, *args):
        ok = False
        inv=self.pool.get('account.invoice')
        for line in self.browse(cr, uid, ids):
            allowed=line.allow_out
            # print allowed
        return allowed

    def _reconciled_check(self, cr, uid, ids, name, args, context=None):
            res = {}
            for id in ids:
                res[id] = self.test_check(cr, uid, [id])
            return res
    def _check_allow_out(self, cr, uid, ids, name, args, context=None):
            res = {}
            for id in ids:
                res[id] = self.test_allowed(cr, uid, [id])
            return res

    _columns = {
        'check_state': fields.function(_reconciled_check, method=True, string='Reglé', type='boolean'),
        'out_allowed': fields.function(_check_allow_out, method=True, string='Sortie Autorisee', type='boolean'),
        'allow_out': fields.boolean('Autorisation de Sortie'),    
        'transmitted': fields.boolean('Transmis'),    
        'name_divers':fields.char('Nom Occasionel', size=64),
        'tel_divers':fields.char('Telephone Occasionel', size=64),
        'address_divers':fields.char('Addresse Occasionel', size=64),   
        'validator':fields.many2one('res.users','Validation'),
        'printed': fields.boolean('Printed'), 
        'reviens_state':fields.selection(
            [('calculated','Revient Theorique'),
             ('fixed','Prix de vente établie'),
             ('confirmed','Confirmé')], 'Calcul du reviens', readonly=True, size=32,),        
        'cur_rate':fields.float('Cours Devise'),
        }
    _defaults = {
        'cur_rate': 1,
    }

    
    def printed(self,cr,uid,ids,context=None):
        return 'Printing'
        
    def create_card_comm(self,cr,uid,ids,context=None):
        obj_product=self.pool.get('product.product')
        obj_inv_line=self.pool.get('account.invoice.line')
        products=obj_product.search(cr, uid, [('default_code','like','FRAISCB%')])
        products=obj_product.browse(cr,uid,products)
        for inv in self.browse(cr,uid,ids):
            a=inv.user_id.shop.x_journal.default_credit_account_id.id
            ht=inv.amount_untaxed
            for p in products:
                if p.default_code=='FRAISCB':
                    obj_inv_line.create(cr, uid, {
                    'name': p.name,
                    'account_id': a,
                    'price_unit': ht*3.25/100,
                    'th_weight':0,
                    'quantity': 1,
                    'discount':0,
                    'invoice_id':inv.id,
                    'uos_id': p.uom_id.id,
                    'product_id': p.id,
                    'invoice_line_tax_id':[(6,0,[25])],                    
                    'account_analytic_id': False,})
                else:
                    obj_inv_line.create(cr, uid, {
                    'name': p.name,
                    'account_id': a,
                    'price_unit': 1800,
                    'th_weight':0,
                    'quantity': 1,
                    'invoice_id':inv.id,
                    'discount':0,
                    'uos_id': p.uom_id.id,
                    'product_id': p.id,
                    'invoice_line_tax_id':[(6,0,[25])],
                    'account_analytic_id': False,})
        return True
    
account_invoice()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns ={
        'local_supplier':fields.boolean('Fournisseur Local'),
        'foreign_supplier':fields.boolean('Fournisseur Import'),
        'group_supplier':fields.boolean('Fournisseur Group'), 
    }
 #   _sql_constraints = [ ('name', 'UNIQUE (name)', 'The name of the partner must be unique !')] 
res_partner()

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    _columns ={
        'move_line':fields.many2one('account.move.line'),
    }
 #   _sql_constraints = [ ('name', 'UNIQUE (name)', 'The name of the partner must be unique !')] 
account_bank_statement_line()


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    def product_discount_change(self, cr, uid, ids, discount,max):
        warning={}
        if discount>max:
            warning = {
                    'title': _('Remise incorrect !'),
                    'message': _('Remise Maximum atteint!!!') 
            }
        user_obj=self.pool.get('res.users')
        user=user_obj.browse(cr,uid,uid)
        if user.x_discount:
            if user.x_discount>0:
                max=user.x_discount
#        if self.browse(cr,uid,ids)[0].invoice_id.type=='out_refund':
#            max=100
        discount=min(discount,max)   
        return {'value':{'discount': discount},'warning':warning}
        
    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
#                if line.product_id.purchase_price:
#                   res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.product_id.purchase_price*line.product_uos_qty), 2)
#                else:
                res[line.id] = round((line.price_unit*line.quantity*(100.0-line.discount)/100.0) -(line.product_id.standard_price*line.quantity), 2)
        return res
    def _product_margin_perc(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
#                if line.purchase_price:
#                    res[line.id] = (round(((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.product_id.purchase_price*line.product_uos_qty))/(line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0), 2))*100
#                else:
                # print line.margin
                # print line.price_unit*line.quantity*(100.0-line.discount)/100.0
                res[line.id] = (round(line.margin/max(0.01,(line.price_unit*line.quantity*(100.0-line.discount)/100.0)), 2))*100
        return res
        
        
    _columns ={
	'marge':fields.float('old_marge'),
        'th_weight':fields.float('M. Linere'),
        'margin': fields.function(_product_margin, type='float', method=True, string='Marge',store=True),
        'margin_perc': fields.function(_product_margin_perc, type='float',method=True, string='% Mar',store=True),
        'location':fields.many2one('stock.location','Emplacement'),

    }

    def onchange_discount_purchase(self,cr,uid,ids,disc,unit_price):
        res={}
        for id in ids:
            res[id]={'x_unit_discount':(unit_price*(100-disc)/100)}
            return res
        return res
        #   _sql_constraints = [ ('name', 'UNIQUE (name)', 'The name of the partner must be unique !')] 
account_invoice_line()

class product_brand(osv.osv):
    _name = "product.brand"
    _description = "Branding"
    _columns={
        'name':fields.char('Marque',size=64),
}
product_brand()

class product_nomenclature(osv.osv):
    _name = "product.nomenclature"
    _description = "Nomenclature"
    _columns={
        'name':fields.char('Nomenclature',size=64),
	'description':fields.char('Description',size=128),
        'custom1':fields.float('Droit Douane'),
        'custom2':fields.float('TVA'),
        'custom3':fields.float('Droit Assisea'),
}
product_nomenclature()


class product_product(osv.osv):
    _inherit = 'product.product'
    _columns ={
        'prix1':fields.float('Prix 1'),
        'prix2':fields.float('Prix 2'),
        'prix3':fields.float('Prix 3'),
        'prix4':fields.float('Prix 4'),
        'prix5':fields.float('Prix 5'),
        'prix6':fields.float('Prix 6'),
        'prix7':fields.float('Prix 7'),
        'prix8':fields.float('Prix 8'),
        'prix9':fields.float('Prix 9'),
        'prix10':fields.float('Prix 10'),
        'prix11':fields.float('Prix 11'),
        'marque':fields.many2one('product.brand', 'Marque'),
	'nomenclature':fields.many2one('product.nomenclature','Nomenclature')
    }
    _sql_constraints = [('ref','unique(ref)', 'Unique!')]
product_product()

class res_company(osv.osv):
    _inherit = 'res.company'
    
    _columns = {
        'local_purchase':fields.char('local_purchase',store=True, size=64),
        'import_purchase':fields.char('import_purchase',store=True, size=64),
    }
res_company()


class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def _amount_residual(self, cr, uid, ids, field_names, args, context=None):
        """
           This function returns the residual amount on a receivable or payable account.move.line.
           By default, it returns an amount in the currency of this journal entry (maybe different
           of the company currency), but if you pass 'residual_in_company_currency' = True in the
           context then the returned amount will be in company currency.
        """
        res = {}
        if context is None:
            context = {}
        cur_obj = self.pool.get('res.currency')
        for move_line in self.browse(cr, uid, ids, context=context):
            res[move_line.id] = {
                'amount_residual': 0.0,
                'amount_residual_currency': 0.0,
                'amount_balance':0,
            }

            if move_line.reconcile_id:
                continue
            if not move_line.account_id.type in ('payable', 'receivable'):
                #this function does not suport to be used on move lines not related to payable or receivable accounts
                continue

            if move_line.currency_id:
                move_line_total = move_line.amount_currency
                sign = move_line.amount_currency < 0 and -1 or 1
            else:
                move_line_total = move_line.debit - move_line.credit
                sign = (move_line.debit - move_line.credit) < 0 and -1 or 1
            line_total_in_company_currency =  move_line.debit - move_line.credit
            context_unreconciled = context.copy()
	    amount_bal=line_total_in_company_currency
            if move_line.reconcile_partial_id:
                for payment_line in move_line.reconcile_partial_id.line_partial_ids:
                    if payment_line.id == move_line.id:
                        continue
                    if payment_line.currency_id and move_line.currency_id and payment_line.currency_id.id == move_line.currency_id.id:
                            move_line_total += payment_line.amount_currency
                    else:
                        if move_line.currency_id:
                            context_unreconciled.update({'date': payment_line.date})
                            amount_in_foreign_currency = cur_obj.compute(cr, uid, move_line.company_id.currency_id.id, move_line.currency_id.id, (payment_line.debit - payment_line.credit), round=False, context=context_unreconciled)
                            move_line_total += amount_in_foreign_currency
                        else:
                            move_line_total += (payment_line.debit - payment_line.credit)
                    line_total_in_company_currency += (payment_line.debit - payment_line.credit)
		    if payment_line.credit!=0:
	            	amount_bal=line_total_in_company_currency

            result = move_line_total
            res[move_line.id]['amount_residual_currency'] =  sign * (move_line.currency_id and self.pool.get('res.currency').round(cr, uid, move_line.currency_id, result) or result)
            res[move_line.id]['amount_residual'] = sign * line_total_in_company_currency
            res[move_line.id]['amount_balance']= amount_bal
            print res[move_line.id]['amount_balance'] 
        return res
    
    
    _columns = {
        'instrument_number':fields.char('Instrument', size=64),
        'bank': fields.many2one('res.bank','Banque'),
        'amount_balance': fields.function(_amount_residual, method=True, string='Solde', multi="residual"),
    }
account_move_line()

class account_move(osv.osv):
    _inherit = 'account.move'
    
    _columns = {
        'ref': fields.char('Reference', size=64,fnct_search=True),
        }
account_move()


class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'location':fields.many2one('stock.location','Emplacement'),
        'shop':fields.many2one('sale.shop','Souche'),
    }
res_users()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'validator':fields.many2one('res.users', 'Validation'),
    }
    def set_location(self, cr, uid, ids,
            name=None, args=None, context=None):
        "Return the total quantity in an invoice"
        prod=self.pool.get('product.product')
        move=self.pool.get('stock.move')
        picking=self.pool.get('stock.picking')
        pickings = self.browse(cr,uid,ids)
        for picking in pickings:
            for move_line in picking.move_lines:
                if not move_line.product_id:
                    continue
                # line.product_id.calculated_cost=l
                # if line.x_move_id:
                if "Arrivage" in move_line.location_dest_id.name:
                    dest=move_line.location_dest_id.chained_location_id.id
                    move.write(cr,uid,move_line.id,{'location_dest_id':dest})
        return True
    def set_force_location(self, cr, uid, ids,
            name=None, args=None, context=None):
        "Return the total quantity in an invoice"
        prod=self.pool.get('product.product')
        move=self.pool.get('stock.move')
        picking=self.pool.get('stock.picking')
        pickings = self.browse(cr,uid,ids)
        for picking in pickings:
            for move_line in picking.move_lines:
                if not move_line.product_id:
                    continue
                # line.product_id.calculated_cost=l
                # if line.x_move_id:
                dest=picking.x_force_destination.id
                move.write(cr,uid,move_line.id,{'location_dest_id':dest})
        return True
        
    def picking_validate(self, cursor, user, ids, args, context=None):
        self.write(cursor, user, ids, {'validator': user})

        warning={}
        warning = {
                'title': _('Validation'),
                'message': _('Document Valide par %s'% user)
        }
	return True	
       # return {'value':{'validator':user}}
stock_picking()

class stock_location(osv.osv):
    _inherit='stock.location'
    
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context:
	    # print 'context',context
            if context.get('shop',False):
                cur_user=self.pool.get('res.users').browse(cr,user,user)
                shop=cur_user.shop.name
                shop='%'+shop+'%'
		# print shop
                return self.pool.get('stock.location').search(cr,user,[('location_id.name','like',shop)])
                #return super(stock_location,self).search(cr, user, args, offset, limit, order,context, count)
            else:
                return super(stock_location,self).search(cr, user, args, offset, limit, order,context, count)
        else:
            return super(stock_location,self).search(cr, user, args, offset, limit, order,context, count)
        
stock_location()
