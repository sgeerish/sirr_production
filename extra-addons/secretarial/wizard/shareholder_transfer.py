# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time

class shareholder_transfer(osv.osv_memory):
    _name = "shareholder.transfer"
    _columns = {
		'partner_id': fields.many2one('res.partner','To Transfer', required=True),	
		'num_shares_transfer': fields.integer('Number of shares to Transfer', required=True),	
        'date': fields.date('Date', required=True),
     }

    def default_get(self, cr, uid, fields, context=None):
        shareholder_obj = self.pool.get('shareholders')
        res = super(shareholder_transfer, self).default_get(cr, uid, fields, context=context)
        if not context:
            context={}
        num_shares = 0    
        if 'date' in fields:
            res.update({'date': time.strftime('%Y-%m-%d')})
        for share in shareholder_obj.browse(cr, uid, context.get('active_ids', []), context=context):
        	num_shares = share.num_shares
        	if share.status == 'transfer':
          		raise osv.except_osv(_('Error !'), _('Can not transfer already transfer share.'))
		if 'num_shares_transfer' in fields:
			res.update({'num_shares_transfer': num_shares})
        return res

    def transfer(self, cr, uid, ids, context):
        shareholder_obj = self.pool.get('shareholders')
        ir_seq_obj = self.pool.get('ir.sequence')
        data = self.read(cr, uid, ids)[0]
        for share in shareholder_obj.browse(cr, uid, context.get('active_ids', []), context=context):
			transfer_share = 0.0
			if data['num_shares_transfer'] == 0:
				continue
			elif data['num_shares_transfer'] > share.num_shares:
				raise osv.except_osv(_('Error'), _('You can not perform this operation transfer share more than avialble share !'))
			elif data['num_shares_transfer'] < share.num_shares:
				reference = ir_seq_obj.get(cr, uid, 'shareholders')
				shareholder_obj.create(cr, uid,{
											'name':share.name.id,
											'num_shares':share.num_shares - data['num_shares_transfer'],
											'certificate_number':share.num_shares + int(reference),
											'distinct_start_number':share.num_shares - data['num_shares_transfer'] + 1,
											'distinct_end_number': share.num_shares,
											'opened_date':time.strftime('%Y-%m-%d'),
										})
			reference = ir_seq_obj.get(cr, uid, 'shareholders')
			if data['num_shares_transfer'] == share.num_shares:
				transfer_share = share.num_shares
			else:
				transfer_share = share.num_shares - data['num_shares_transfer']
					
			shareholder_obj.create(cr, uid,{
										'name':data['partner_id'],
										'num_shares':transfer_share,
										'certificate_number':share.num_shares + int(reference),
										'distinct_start_number':1,
										'distinct_end_number': transfer_share,
										'opened_date':time.strftime('%Y-%m-%d'),
									})
			shareholder_obj.write(cr, uid, [share.id], {'status':'transfer'}, context)
        return {}

shareholder_transfer()

