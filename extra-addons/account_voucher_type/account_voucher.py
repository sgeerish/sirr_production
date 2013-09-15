# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime

class account_voucher_type(osv.osv):
    _name = "account.voucher.type"
    _description = "Type de paiement"
    _columns = {
        'name' : fields.char('Nom', size=32, required=True),
	'account_id':fields.many2one('account.account','Compte')
        
    }
account_voucher_type()

class account_voucher(osv.osv):
    """ CRM Meeting Cases """

    _inherit = 'account.voucher'
    
    _columns = {
        'voucher_type_id':fields.many2one('account.voucher.type','Type de transaction'),
    }

account_voucher()
