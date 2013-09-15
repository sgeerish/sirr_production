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

class fleet_service_items(osv.osv):
    _name = "fleet.service.items"
    _description="Different types of service tasks"
    _columns={
              'name':fields.char('Service Item',size=30,required=True),
              'itemtype':fields.selection([
                                         ('normal','Normal'),
                                         ('fluids','Fluids'),
                                         ('inspection','Inspection'),
                                         ('replace','Replace'),
                                         ('others','Others')],'Type of Service'),
              'freqn':fields.integer('Frequency'),
              'freqz':fields.selection([('days','Days'),
                                        ('weeks','Weeks'),
                                        ('months','Months'),
                                        ('years','Years')
                                        ]),
              'freqd':fields.float('Mileage', digits=(10,3)),
              'freqdz':fields.selection([
                                         ('miles','Miles'),
                                         ('km','Kilometers'),
                                         ('hours','Hours')
                                         ]),
               'sparesreq':fields.one2many('fleet.service.items.spares','serviceitem','Spares Required')
               
}
    _defaults = {
                 'freqdz':lambda *a:'km',
                 'freqz':lambda *a:'days',
                 'itemtype':lambda *a:'inspection'
                 }
fleet_service_items()

class fleet_service_items_spares(osv.osv):
    _name="fleet.service.items.spares"
    _description="Service items to spare relation"
    
    def fetchunit(self,cr,uid,ids,productid):
        #print "Control is txed & Product id"
        #print productid
        if productid:
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, productid,False)
            #print product_obj
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            #print default_uom
            res={}
            res['unit']=default_uom
            #print res
            return {'value':res}
        else:
            return False
    
    _columns={
              'product':fields.many2one('product.product','Spare Part',domain="[('spare_ok','=','True')]",required=True),
              'qtyreqd':fields.float('Quantity',digits=(10,3),required=True),
              #'unit':fields.function(defaultuom,method=True,store=True,string="Unit of Use(Default)"),
              'unit':fields.many2one('product.uom','Unit Of Use'),
              'serviceitem':fields.many2one('fleet.service.items','Service Item')
              }
fleet_service_items_spares()

class fleet_service_templ(osv.osv):
    _name = 'fleet.service.templ'
    _description='The Template is a collection of service items.'
    _columns={
              'name':fields.char('Template Name',size=50,required=True,select=1,help="Service Templates are a collection of Service Tasks for a specific category of vehicles."),
              'description':fields.char('Description',size=50,required=True,select=1),
              'items':fields.many2many('fleet.service.items','fleet_template_tasks_rel','template_id','item_id','Service Items'),
              }
fleet_service_templ()