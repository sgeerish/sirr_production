# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime
class account_move(osv.osv):
    _inherit="account.move"
    _columns={
        'tax_id':fields.many2one('account.tax','Taxe'),
    }

    def split(self, cr, uid, ids, *args):
        move_line_obj=self.pool.get('account.move.line')
        for voucher in self.browse(cr,uid,ids):
            if voucher.tax_id:
                for move in voucher.line_id:
                    if move.debit>0:
                        amount=move.debit
                        move2=move_line_obj.copy(cr,uid,move.id)
                        amount_untaxed=amount/1.20
                        amount_tax=amount*0.20
                        move_line_obj.write(cr,uid,move.id,{'debit':amount_untaxed})
                        move_line_obj.write(cr,uid,move2,{'debit':amount_tax,'account_id':voucher.tax_id.account_paid_id.id})
        return True
account_move()
