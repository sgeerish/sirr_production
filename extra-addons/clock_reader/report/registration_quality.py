# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import time
import pooler
import datetime
from report import report_sxw
from types import NoneType

__sql_registration_quality__ = '''
SELECT leg, name, count(a), count(k), count(fp), count(n)
FROM (
SELECT E.otherid as leg, E.name as name, A.name as a, CAST(Null as timestamp)
    as k, CAST(Null as timestamp) as fp, CAST(Null as timestamp) as n
FROM
	hr_employee as E
	left outer join
	hr_attendance as A
	on E.id = A.employee_id
where A.method='automatic'
    and ('%(dstart)s'::date,'%(dend)s'::date) overlaps (A.name,A.name)
union
SELECT E.otherid, E.name, Null, A.name, Null, Null
FROM
	hr_employee as E
	left outer join
	hr_attendance as A
	on E.id = A.employee_id
where A.method='keyboard'
    and ('%(dstart)s'::date,'%(dend)s'::date) overlaps (A.name,A.name)
union
SELECT E.otherid, E.name, Null, Null, A.name, Null
FROM
	hr_employee as E
	left outer join
	hr_attendance as A
	on E.id = A.employee_id
where A.method='fingerprint'
    and ('%(dstart)s'::date,'%(dend)s'::date) overlaps (A.name,A.name)
union
SELECT E.otherid, E.name, Null, Null, Null, A.name
FROM
	hr_employee as E
	left outer join
	hr_attendance as A
	on E.id = A.employee_id
where A.method is Null
    and ('%(dstart)s'::date,'%(dend)s'::date) overlaps (A.name,A.name)
) AS T
GROUP BY leg,name
'''

class registration_quality(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(registration_quality, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines':self._lines,
            'totals':self._totals,
        })

    def _lines(self):
        date_from = self.datas['form']['date_from']
        date_to = self.datas['form']['date_to']

        self.cr.execute(__sql_registration_quality__ % {'dstart': date_from,
                                                        'dend': date_to})
        lines = self.cr.fetchall()

        self.t_auto = 0
        self.t_keyb = 0
        self.t_fgpr = 0
        self.t_none = 0

        res = []
        for id, employee, c_auto, c_keyb, c_fgpr, c_none  in lines:
            r = {
                'id': id,
                'name': employee,
                'c_auto': c_auto,
                'c_keyb': c_keyb,
                'c_fgpr': c_fgpr,
                'c_none': c_none,
                'efectivity': "%.3f" % (float(c_keyb + c_fgpr) / float(c_auto +
                                                                       c_keyb +
                                                                       c_fgpr +
                                                                       c_none)
                                        * 100.),
            }
            res.append(r)
            self.t_auto += c_auto
            self.t_keyb += c_keyb
            self.t_fgpr += c_fgpr
            self.t_none += c_none

        return res

    def _totals(self):
        tt =  float(self.t_auto+self.t_keyb+self.t_fgpr+self.t_none) * 100
        if tt == .0:
            return (self.t_auto, self.t_keyb, self.t_fgpr, self.t_none, 'inv')
        else:
            return (self.t_auto, self.t_keyb, self.t_fgpr, self.t_none,
                    "%.3f" % (float(self.t_keyb+self.t_fgpr) / tt))

report_sxw.report_sxw('report.clock_reader.registration_quality_report',
                      'hr.attendance',
                      'addons/clock_reader/report/registration_quality.rml',
                      parser=registration_quality)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


