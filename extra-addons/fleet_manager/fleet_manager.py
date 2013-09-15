# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv, fields
import pooler
import time
import datetime
import fleet_service


class fleet_vehicles(osv.osv):
    _name = "fleet.vehicles"
    _description = "Holds records of Vehicles"
    def copy(self, cr, uid, id, default=None,context={}):
        if not default:
            default = {}
        default.update({
            'name':'New Vehicle Name',
            'regnno':'New Registration no',
        })
        return super(fleet_vehicles, self).copy(cr, uid, id, default, context)
    
    #def _lastodometer(self,cr,uid,ids,context={}):
   #     return(0.00)
    #def _lastododate(self,cr,uid,ids,context={}):
    #    datetime.datetime.now()
    
    
    _columns = {
                'name':fields.char('Vehicle Name',size=20,required=True),
                'regnno':fields.char('Vehicle Registration #',size=11,required=True),
                'company':fields.many2one('res.company','Company',required=True),
                'assetacc':fields.many2one('account.account',string='Asset Account',domain=[('type','=','vehicle')],required=True),
                'depracc':fields.many2one('account.account',string='Depreciation Account',required=True),
                'year':fields.char('Year',size=4),
                'make':fields.char('Make',size=10),
                'model':fields.char('Model',size=15),
                'serial':fields.char('productSerial #',size=50),
                'type': fields.many2one('fleet.type', string='Class', required=True),
                'status': fields.selection([
                        ('active','Active'),
                        ('inactive','InActive'),
                        ('outofservice','Out of Service'),                        
                        ], 'status', required=True,),
                'ownership': fields.selection([
                        ('owned','Owned'),
                        ('leased','Leased'),
                        ('rented','Rented'),                       
                        ], 'Ownership', required=True), 
                'schedname':fields.many2one('fleet.service.templ','PM Schedule',help="Preventive maintainance schedule for this vehicle",required=True),
                'cmil':fields.float('Current Mileage',digits = (16,3)),
                'bmil':fields.float('Base Mileage',digits=(16,3),help="The last recorded mileage"),
                'bdate':fields.date('Recorded Date',help="Date on which the mileage is recorded"),
                'pdate':fields.date('Purchase Date',help="Date of Purchase of vehicle"),
                'pcost':fields.float('Purchase Value',digits=(16,2)),
                'ppartner':fields.many2one('res.partner','Purchased From'),
                'pinvoice':fields.char('Purchase Invoice',size=15),
                'podometer':fields.integer('Odometer at Purchase'),
                'startodometer':fields.integer('Start Odometer',required=True),
                #'lastodometer':fields.function(_lastodometer , method=True ,string='Last Odometer',digits=(11,0)),
                #'lastrecdate':fields.function(_lastododate , method=True , string='on date'),
                'deprecperc':fields.float('Depreciation in %',digits=(10,2),required=True),
                'deprecperd':fields.selection([
                                               ('monthly','Monthly'),
                                               ('quarterly','Quarterly'),
                                               ('halfyearly','Half Yearly'),
                                               ('annual','Yearly')
                                               ],'Depr. period',required=True),
                'primarymeter':fields.selection([
                                                 ('odometer','Odometer'),
                                                 ('hourmeter','Hour Meter'),
                                                 ],'Primary Meter',required=True),
                'fueltype':fields.selection([
                                             ('petrol','Petrol'),
                                             ('diesel','Diesel'),
                                             ('gasoline','Gasoline'),
                                             ('cng','C.N.G'),
                                             ('lpg','L.P.G')
                                             ],'Fuel Used',required=True),
                #'fuelcardno':fields.one2one('fleet.fuelcards','Fuel Card #'),
                'fueltankcap':fields.float('Fuel Tank Capacity'),
                'warrexp':fields.date('Date',help="Expiry date for warranty of product"),
                'warrexpmil':fields.integer('(or) Mileage',help="Expiry mileage for warranty of product"),
                'location':fields.many2one('stock.location','Stk Location',help="Select the stock location or create one for each vehicle(recommended) so that the spares, tyres etc are assossiated with the vehicle when issued",required=True),
                
                
                }
    _defaults={
               'status':lambda *a:'active',
               'ownership':lambda *a:'owned',
               'fueltype':lambda *a:'diesel',
               'primarymeter':lambda *a:'odometer',
               'deprecperd':lambda *a:'annual'
               }

        
    _sql_constraints = [
        ('uniq_regn_no', 'unique (regnno)', 'The registration no of the vehicle must be unique !')
    ]
    
fleet_vehicles()

class fleet_type(osv.osv):
    #This module will 
    _name = "fleet.type"
    _columns = {
             'name': fields.char('Intitule', size=64,required=True),
}
fleet_type()    
class account_account(osv.osv):
    #This module will 
    _inherit = "account.account"
    _columns = {
             'type': fields.selection([
            ('receivable','Receivable'),
            ('payable','Payable'),
            ('view','View'),
            ('consolidation','Consolidation'),
            ('other','Others'),
            ('closed','Closed'),
            ('vehicle','Vehicle'),
        ], 'Internal Type', required=True,),
}
account_account()



class product_product(osv.osv):
    _name="product.product"
    _description="product fleet enhancements"
    _inherit="product.product"
    _columns={
              'spare_ok': fields.boolean('Is a vehicle spare', help="Determines if the product is a vehicle spare."),
              }
product_product()

class res_partner_address(osv.osv):
    _description ='Partner Addresses with fleet enhancements'
    _name = 'res.partner.address'
    _order = 'id'
    _inherit='res.partner.address'
    _columns = {
                'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'),('origin','Origin'),('destination','Destination'), ('other','Other') ],'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),
                }
res_partner_address()
                
class fleet_fuellog(osv.osv):
    _name = "fleet.fuellog"
    _description = "Records the fuelling entries"
    _rec_name="vehicle"
    
    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False
    
    def cancel_voucher(self,cr,uid,ids,context={}):
        self.action_cancel(cr, uid, ids)
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
        
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    def calc_amount(self,cr,uid,ids,totalcost,qty):
        res={}
        #print "totalcost>>",totalcost
        #print "qty>>>",qty
        if qty:
            res['costpl'] = totalcost/qty
        else:
            res['costpl']=0.0
        #print "costpl>>>",costpl       
#        self.write(cr,uid,ids,{'costpl':costpl}) 
        return {'value':res}
    def calc_amount2(self,cr,uid,ids,field,unknown,context={}):
        res={}
        for obj in self.browse(cr,uid,ids):
            
        #print "totalcost>>",totalcost
        #print "qty>>>",qty
            if obj.qty:
                res[obj.id] = obj.totalcost/obj.qty
            else:
                res[obj.id]=0.0
        #print "costpl>>>",costpl       
#        self.write(cr,uid,ids,{'costpl':costpl}) 
        return res
        
    def _get_journal(self, cr, uid, context):
        type_inv = context.get('type', 'rec_voucher')
        journal_obj = self.pool.get('account.journal')
        res = False
        res = journal_obj.search(cr, uid, [('type', '=', 'purchase')], limit=1)
        if res:
            return res[0]
        else:
            return False
        
    def _get_currency(self, cr, uid, context):
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid])[0]
        if user.company_id:
            return user.company_id.currency_id.id
        else:
            return pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('rate','=',1.0)])[0]

    def copy(self, cr, uid, id, default=None,context={}):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'log_no': self.pool.get('ir.sequence').get(cr, uid, 'fleet.fuel'),
            'move_id':False,
        })
        return super(fleet_fuellog, self).copy(cr, uid, id, default, context)

    _columns = {
                'log_no':fields.char('Log Entry#',size=12),
                'vehicle':fields.many2one('fleet.vehicles','Vehicle Name',required=True),
                'vendor':fields.many2one('res.partner','Fuel Station',required=True),
                'date':fields.date('Date',required=True),
                'invno':fields.char('Invoice no',size=10,required=True),                
                'costpl':fields.function(calc_amount2,method=True,string='Cost Per Ltr',digits=(16,2),store=True),
                'qty':fields.float('Quantity',digits=(16,3),required=True),
                'totalcost':fields.float('Total Cost',digits=(16,2),required=True),
                'odometer':fields.integer('Odometer',required=True),
                'emp_resp':fields.many2one('hr.employee','Employee Responsible',required=True,help="Employee reporting fuelling details"),
                'driver':fields.many2one('hr.employee','Driver',required=True,help="Driver who has driven the vehice before this fuelling"),
                'currency_id': fields.many2one('res.currency', 'Currency',),
                'journal_id':fields.many2one('account.journal', 'Journal', required=True,),
                'move_id':fields.many2one('account.move', 'Account Entry',readonly=True),
                'period_id': fields.many2one('account.period', 'Period', required=True,),
                'state':fields.selection([
                                          ('draft','Draft'),
                                          ('cancel','Cancel'),
                                          ('proforma','Proforma'),
                                          ('posted','Posted')
                                          ],readonly=True)

                #'voucher':fields.many2one('account.voucher','Rel Voucher',domain=[('state','=','posted')],help="Select the related accounts voucher"),
                }
    _defaults = {
        'date' : lambda *a: time.strftime('%Y-%m-%d'),
        'period_id': _get_period,
        'journal_id':_get_journal,
        'currency_id': _get_currency,
        'state': lambda *a:'draft',
        'log_no': lambda obj,cr,uid,context: obj.pool.get('ir.sequence').get(cr,uid,'fleet.fuel'),
    }
    
    #This function is used for transition from draft to proforma
    def open_fuellog(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'proforma'})
        
    def unlink(self, cr, uid, ids):
        vouchers = self.read(cr, uid, ids, ['state'])
        unlink_ids = []
        for t in vouchers:
            if t['state'] in ('draft', 'cancel'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv('Invalid action !', 'Cannot delete invoice(s) which are already opened or paid !')
        osv.osv.unlink(self, cr, uid, unlink_ids)
        return True
    
    #This function is used to set the state to cancelled
    def cancel_voucher(self,cr,uid,ids,context={}):    
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
    def _cancel_moves(self,cr,uid,ids,context={}):
        for obj in self.browse(cr, uid, ids):
            self.pool.get('account.move').unlink(cr,uid,[obj.move_id.id])
        return self.write(cr,uid,ids,{'state':'cancel'})
    #This function will create a new account move and the corresponding account move lines
    def _create_moves(self,cr,uid,ids,context={}):
        for log in self.browse(cr,uid,ids):
            journal = self.pool.get('account.journal').browse(cr, uid, log.journal_id)
            name=False
            if journal.sequence_id:
                name = self.pool.get('ir.sequence').get_id(cr, uid, journal.sequence_id.id)
                move = {'name': name, 'journal_id': log.journal_id.id}
            else:
                move = {'name': 'Fuel'+str(log.id), 'journal_id': log.journal_id.id}
            move['period_id'] = log.period_id.id
            #print ">>>",move
            move_id = self.pool.get('account.move').create(cr, uid, move)
            debit_move_line = {
                'name': log.vehicle.id,
                'debit': log.totalcost,
                'credit':False,
                'account_id': log.journal_id.default_debit_account_id.id or False,
                'move_id':move_id ,
                'journal_id':log.journal_id.id ,
                'period_id':log.period_id.id,
                'partner_id': log.vendor.id,
                'ref': str(log.id)+log.vehicle.name, 
                'date': log.date
            }
            self.pool.get('account.move.line').create(cr,uid,debit_move_line)
            credit_move_line = {
                'name': log.vehicle.id,
                'debit': False,
                'credit':log.totalcost,
                'account_id': log.vendor.property_account_payable.id or False,
                'move_id':move_id ,
                'journal_id':log.journal_id.id ,
                'period_id':log.period_id.id,
                'partner_id': log.vendor.id,
                'ref': str(log.id)+log.vehicle.name, 
                'date': log.date
            }
            #print "credit_move_line>>>",credit_move_line
            self.pool.get('account.move.line').create(cr,uid,credit_move_line)
            self.write(cr,uid,log.id,{'move_id':move_id,'state':'posted'})
        return True

fleet_fuellog()

class fleet_odometer(osv.osv):
    _name = "fleet.odometer"
    _description = "Recording of daily odometer reading"
    _rec_name = "vehicle"
    _columns = {
                'vehicle':fields.many2one('fleet.vehicles','Vehicle Name',required=True),
                'date':fields.date('Date',required=True),
                'odometer':fields.integer('Odometer',required=True),
                'emp_resp':fields.many2one('hr.employee','Employee Responsible',required=True),                
                }
fleet_odometer()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

