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

import time
import datetime
import tools
import pooler
import netsvc
from mx import DateTime
from osv import osv,fields
logger = netsvc.Logger()

from report import report_sxw

class pricelist_ver(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(pricelist_ver, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
		'time':time,
            	'get_qty':self._get_qty,
		'get_total':self._get_total
        })
        self.context = context

    def _get_total(self,object):
	return 0
    def _get_qty(self,item):
        product=item.product_id.id
        start=DateTime.strptime(item.price_version_id.date_start,'%Y-%m-%d')
        end=DateTime.strptime(item.price_version_id.date_end,'%Y-%m-%d')
	qty=self.pool.get('sale.report').search(self.cr,self.uid,[
					('product_id','=',product),
					('date','>=',start.date),
					('date','<=',end.date)
					])
	if qty==[]:
		return {'quantity':0,'value':0}
	else:
		quantity=0
		value=0
		datas=self.pool.get('sale.report').read(self.cr,self.uid,qty,['product_uom_qty','price_total'])
		for data in datas:
			quantity+=data['product_uom_qty']
			value+=data['price_total']*data['product_uom_qty']
        	return {'quantity':quantity,'value':value}
        
report_sxw.report_sxw('report.product.pricelist.version.rndLNpBi', 'product.pricelist.version', '', parser=pricelist_ver)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
