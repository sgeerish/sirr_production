# -*- encoding: utf-8 -*-
##############################################################################
#
#    Clock Reader for OpenERP
#    Copyright (C) 2004-2009 Moldeo Interactive CT
#    (<http://www.moldeointeractive.com.ar>). All Rights Reserved
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
import netsvc
import timeutils as tu

logger = netsvc.Logger()

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = "hr.contract"
    _columns = {
        'turn_id' : fields.many2one('hr.timesheet.group', 'Turn', select=True),
        'department_id' : fields.many2one('hr.department', 'Department', select=True),
    }
    def get_turn(self, cr, uid, ids, date, context=None):
        res = {}
        if isinstance(date, str):
            date = tu.dt(date)
        for cont in self.browse(cr, uid, ids):
            if (tu.d(cont.date_start) <= date and
                (cont.date_end == False or date <= tu.d(cont.date_end))):
                    ts = filter(lambda i:
                        i.dayofweek == str(date.weekday()) or i.dayofweek == '',
                                           cont.turn_id.timesheet_id)
                    if len(ts) == 1:
                        ddate = tu.datetime.combine(date.date(), tu.time(0))
                        res[cont.id] = (ddate +
                                        tu.timedelta(hours=ts[0].hour_from),
                                        ddate +
                                        tu.timedelta(hours=
                                        24 * (ts[0].hour_from >
                                              ts[0].hour_to) + ts[0].hour_to))
                    elif len(ts) > 1:
                        raise RuntimeError("More than one turn enabled at same time. See Timesheet line.")
                    else:
                        res[cont.id] = False
            else:
                res[cont.id] = False
        return res
hr_contract()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _description = 'hr.employee'

    def get_attendance_days(self, cr, uid, ids, daterange=[], context=None):
        """
        Return all attendances of this employee
        """
        res = {}
        if len(daterange) == 2:
            daterange = [('date', '>=', str(daterange[0])),
                         ('date', '<=', str(daterange[1]))] 
        else:
            daterange=[]
        for emp in self.browse(cr, uid, ids):
            journal_ids = self.pool.get('hr.journal').search(cr,uid,
                [('employee_id', '=', emp.id)]+daterange, context=context)
            res[emp.id] = self.pool.get('hr.journal').browse(cr, uid, journal_ids,
                                                context=context)
        return res

    def get_valid_holidays(self, cr, uid, ids, date, context=None):
        res = {}

        _query_ = """
            SELECT employee_id, id, state
            FROM hr_holidays
            WHERE
                employee_id in (%(employee)s) AND
                (
                SELECT CASE
                WHEN not date_to is Null THEN
                    (date_from, date_to)
                    overlaps
                    (DATE '%(date)s', DATE '%(date)s')
                ELSE
                    date_from <= DATE '%(date)s'
                END
                )
            UNION
            SELECT E.e, H.id, H.state
            FROM hr_holidays as H,
                 (VALUES %(employee_x)s) as E(e)
            WHERE
                H.employee_id is Null AND
                (
                SELECT CASE
                WHEN not H.date_to is Null THEN
                    (H.date_from, H.date_to)
                    overlaps
                    (DATE '%(date)s', DATE '%(date)s')
                ELSE
                    H.date_from <= DATE '%(date)s'
                END
                )
            """ % {
                'employee': ','.join(map(str, ids)),
                'employee_x': '(' + '),('.join(map(str, ids)) + ')',
                'date': tu.dt2s(date),
        }
        cr.execute(_query_)
        emp_hol = cr.fetchall()
        for (emp_id, hol_id, state) in emp_hol:
            if not emp_id in res: res[emp_id] = {'draft': [], 'confirm': [],
                                                 'refuse': [], 'validate': [],
                                                 'cancel': []}
            res[emp_id][state].append(hol_id)
        return res

    def get_valid_contract(self, cr, uid, ids, date, context=None):
        res = {}

        _query_ = """
            SELECT employee_id, min(id), count(*) FROM hr_contract
            WHERE
                employee_id in (%(employee)s) AND
                (
                SELECT CASE
                WHEN not date_end is Null THEN
                    (date_start, date_end)
                    overlaps
                    (DATE '%(date)s', DATE '%(date)s')
                ELSE
                    date_start <= DATE '%(date)s'
                END
                )
            GROUP BY
                employee_id
            """ % {
                'employee': ','.join(map(str, ids)),
                'date': tu.dt2s(date),
                }
        cr.execute(_query_)
        emp_con = cr.fetchall()
        for (emp_id, con_id, c) in emp_con:
            if c > 1:
                raise RuntimeError('More than one contract at same time for'
                                   ' employee with id=%i' % emp_id)
            else:
                res[emp_id] = con_id
        return res
hr_employee()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
