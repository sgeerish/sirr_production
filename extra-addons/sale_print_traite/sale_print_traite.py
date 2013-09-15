from osv import fields, osv
import datetime
from datetime import date
from mx import DateTime
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_invoice(osv.osv):
    _inherit="account.invoice"
    def create_traite_line(self,cr, uid, ids, context=None, interval=1):
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.traite_date_start, '%Y-%m-%d')
            count=0
            while count<fy.months:
                self.pool.get('traite.line').create(cr, uid, {
                    'name': fy.id,
                    'date': ds.strftime('%Y-%m-%d'),
                    'amount': fy.amount_total/fy.months,
                })
                ds = ds + relativedelta(months=interval)
                count=count+1
        return True
        
    _columns = {
        'traite_date_start':fields.date('Date debut'),
        'months':fields.float('Mensualites'),
        'tire':fields.char('Nom&Add. Tire',size=128),
        'traite_line': fields.one2many('traite.line', 'name', 'Traites'),
        'bank':fields.char('Banque',size=64),
        'agence':fields.char('Agence',size=64),
        'compte':fields.char('Compte',size=64),
        'rib':fields.char('RIB',size=64),
        
    }
account_invoice()

class traite_line(osv.osv):
    _name="traite.line"
    _columns = {
        'name': fields.many2one('account.invoice', 'Facture'),    
        'date':fields.date('Date'),
        'amount':fields.float('Montant'),        
    }
traite_line()