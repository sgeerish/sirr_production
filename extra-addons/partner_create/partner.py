# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime
class customer_city(osv.osv):
	_name="customer.city"
	_columns={
		'name':fields.char('Nom',size=32),
		'code':fields.char('Code client',size=10),
		'sequence':fields.char('Sequence',size=10),
	}
customer_city()
class customer_create_request(osv.osv):
    _name="customer.create.request"
    _columns={
        'date':fields.date('Date'),
        'name':fields.char('Nom/Raison Sociale',size=64),
        'add1':fields.char('Rue',size=64),
        'add2':fields.char('Rue 2',size=64),
        'city':fields.many2one('customer.city','Ville'),
	'postal_code':fields.char('Code Postal',size=32),
	'contact':fields.char('Dirigeant',size=32),
	'fonction':fields.char('Fonction',size=64),
        'phone':fields.char('Telephone',size=64),
        'mobile':fields.char('Mobile',size=64),
        'country':fields.many2one('res.country','Pays'),
        'contact':fields.char('Nom de Contacte',size=64),
        'nif':fields.char('NIF',size=64),
        'stat':fields.char('STAT',size=64),
        'cif':fields.char('CIF',size=64),
        'rc':fields.char('RC',size=64),
        'email':fields.char('Email',size=64),
        'bank':fields.many2one('res.bank','Banque'),
        'account':fields.char('Numero de Compte',size=64),
        'credit_limit':fields.float('Plafond Demande'),
        'payment_term':fields.many2one('account.payment.term','Condition de Reglement'),
        'creation':fields.many2one('res.users','Demandeur'),
        'sc':fields.many2one('res.users','Service Commerciale'),
        'daf':fields.many2one('res.users','DAF'),
        'direction':fields.many2one('res.users','Direction'),
        'ref':fields.char('Code',size=32),
	'bc1':fields.char('Nom',size=64),
	'company':fields.boolean('Personne Morale'),
        'state':fields.selection([('draft','Brouillon'),
             ('open','Ouverte'),
             ('done','Termine')], 'State', readonly=True, size=32,)
    }
    _defaults={
        'creation':lambda obj, cr, uid, context: uid,
        'state':'draft',
    }
    
    def sc(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'sc': uid})
        
    def daf(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'daf': uid}) 
        
    def user(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'daf': uid,'state':'open'})
        
    def direction(self, cr, uid, ids, *args):
        partner_obj=self.pool.get('res.partner')
        partner_address_obj=self.pool.get('res.partner.address')
        self.write(cr, uid, ids, {'direction': uid,'state':'done'})
        for item in self.browse(cr,uid,ids):
            code=self.pool.get('ir.sequence.type').search(cr,uid,[('code','=',item.city.name)])
            if code==[]:
                ref=self.pool.get('ir.sequence').get(cr, uid, 'code.client')
            else:
	        ref=self.pool.get('ir.sequence').get(cr, uid, item.city.name) #or self.pool.get('ir.sequence').get(cr, uid, 'code.client')
            address=partner_address_obj.create(cr,uid,{
            'active':True,
            'city':item.city.name,
            'country_id':item.country.id,
            'email':item.email,
            'street':item.add1,
            'street2':item.add2,
            'phone':item.phone,
            'mobile':item.mobile,
            'name':item.contact,
            'type':'default',
            }
            )
            val={
            'name':item.name,
            'ref':ref,
            'customer':True,
            'supplier':False,
            'address':[(6, 0, [address])],
            'x_rcs':item.rc,
            'x_nif':item.nif,
            'x_stat':item.stat,
            'x_cif':item.cif,
            'property_payment_term':item.payment_term.id,
            'credit_limit':item.credit_limit,
            }
            partner=partner_obj.create(cr,uid,val)
            partner_address_obj.write(cr,uid,address,{'partner_id':partner})
        view={
            'name':'Client',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': str([('name', '=', item.name)]),
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
	    'views':[(134,'tree'),(135,'form')]
        }
        return view
        
customer_create_request()
