# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Smartmode LTD (<http://www.smartmode.co.uk>).
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

from osv import osv
import netsvc

from urllib2 import urlopen
from datetime import date
import logging


class res_currency(osv.osv):
    _inherit = 'res.currency'
    _the_logger = logging.getLogger('res.currency.updater')

    def update_rates(self, cr, uid, ids=[], context={}):
        self._the_logger.warning('Running update rates.')
        res_log_obj = self.pool.get('res.log')
        curr_rate_obj = self.pool.get('res.currency.rate')

        curr_base_id = self.search(cr, uid, [('base', '=', True)])
        if curr_base_id:
            curr_base = self.read(cr, uid, curr_base_id, ['name'])[0]['name']
        else:
            curr_base = "MGA"

        for curr in self.browse(cr, uid, self.search(cr, uid, [])):
            if curr.base: continue
            req = 'http://finance.yahoo.com/d/quotes.csv?s=%s%s=X&f=l1d1'\
                %(curr_base, curr.name)
            try:
                rate, d = urlopen(req).read().split(',')                    
                d = d.split('/')
                month = int(d[0][1:])
                day = int(d[1])
                year = int(d[2][:4])
                date_str = date(year, month, day).strftime('%Y-%m-%d')
            except Exception, e:
                self._the_logger.error('Error in currency rates updater for "%s%s": %s' %(curr_base, curr.name,  e))
                res_log_obj.create(cr, uid, {
                    'name': 'Error in currency rates updater for "%s%s": %s'
                    %(curr_base, curr.name,  e),
                    'res_model': 'res.currency',
                    'res_id': curr.id
                    })
                continue
            today = date.today().strftime('%Y-%m-%d')
            if round(float(rate), 6)==float(curr.rate) and today!=date_str:
                
                self._the_logger.debug('rate for today=%s date=%s is the same. Leaving previous value' %(today, date_str))
                self._the_logger.debug('rate=%s curr.rate=%s' % (rate, curr.rate))
                continue

            curr_rate_date_curr_ids = curr_rate_obj.search(cr, uid, [('name', '=', date_str),('currency_id', '=', curr.id)])
            if curr_rate_date_curr_ids:
                self._the_logger.debug('date_str=%s + currency_id=%s + currency_name=%s already in db updating instead of creating...' %(date_str, curr.id, curr.name))
                self._the_logger.debug('present record ids are %s' % str(curr_rate_date_curr_ids) )

                curr_rate_obj.write(cr, uid, curr_rate_date_curr_ids, {'rate': rate,})
                continue
            
            self._the_logger.debug('Adding new rate values to the db.')
            curr_rate_obj.create(cr, uid, {
                'name': date_str ,
                'rate': rate,
                'currency_id': curr.id
                })

        res_log_obj.create(cr, uid, {
            'name': 'Currency rates updated.', 
            'res_model': 'res.currency'}
            )

        return True

res_currency()
