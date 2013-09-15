# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime

class vehicle_brand(osv.osv):
    _name = "vehicle.brand"
    _description = "Marque"
    _columns = {
        'name' : fields.char('Nom', size=32, required=True),
        'model' : fields.char('Nom', size=32, required=True),
               
    }
vehicle_brand()

class partner_machine(osv.osv):
    _name = "partner.machine"
    _description = "Machine Client"
    _columns = {
        'name' : fields.char('Matriculation/Serie', size=32, required=True),
        'partner_id':fields.many2one('res.partner','Client',required=True),
        'user_id':fields.many2one('res.users','Commerciale'),
        'description':fields.char('Description', size=64, required=True),
        'vehicle_brand_id':fields.many2one('vehicle.brand','Marque'),
        'note' : fields.text('Note'),
        
    }
partner_machine()

class intervention_type(osv.osv):
    _name = "intervention.type"
    _description = "Type d'intervention"
    _columns = {
        'name' : fields.char('Nom', size=32, required=True),
        
    }
intervention_type()

class small_expenses(osv.osv):
    _inherit = "small.expenses"    
    _columns = {
        'meeting_id' : fields.many2one('crm.meeting','Travaux'),
    }
small_expenses()

class stock_picking(osv.osv):
    _inherit = "stock.picking"    
    _columns = {
        'meeting_id' : fields.many2one('crm.meeting','Travaux'),
    }
stock_picking()

class crm_meeting(osv.osv):
    """ CRM Meeting Cases """

    _inherit = 'crm.meeting'
    
    _columns = {
        'number' : fields.char('Numero', size=32, required=True , readonly=True),    
        'partner_machine_id':fields.many2one('partner.machine','Machine/Vehicule'),
        'counter_start':fields.float('Compteur Debut'),
        'counter_end':fields.float('Compteur End'),
        'phone':fields.char('Telephone', size=32, required=True),
        'intervention_type_id':fields.many2one('intervention.type','Type Intervention'),
        'expense_ids':fields.one2many('small.expenses','meeting_id','Decaissements'),
        'picking_ids':fields.one2many('stock.picking','meeting_id','Sortie de Pieces'),        
    }
    _defaults = {
        'number': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'crm.garage'),
    }
crm_meeting()
