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
from interface import Interface
import netsvc
import timeutils as tu
from tools.translate import _

logger = netsvc.Logger()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _name = "hr.attendance"

    def _get_contract(self, cr, uid, ids, field_name, arg, context=None):
        _query_ = """
            SELECT
                A.id, C.id
            FROM
                hr_attendance as A,
                hr_contract as C
            WHERE
                (((not C.date_end is Null) and
                  (C.date_start, C.date_end) OVERLAPS (A.name, A.name)) OR
                (C.date_end is Null and C.date_start <= A.name)) AND
                (A.employee_id = C.employee_id) AND
                A.id in ( %s )
        """ % ",".join(map(str, ids))
        cr.execute(_query_)
        return dict(cr.fetchall())

    def _get_turn_start(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        conts = self._get_contract(cr, uid, ids, 'contract', None, context=context)
        items = conts.items()
        if len(items) == 0: return False
        att_ids, con_ids = tuple(map(list, zip(*items)))
        cons = self.pool.get('hr.contract').browse(cr, uid, con_ids)
        atts = self.pool.get('hr.attendance').browse(cr, uid, att_ids)
        for (att, cont) in zip(atts, cons):
            turns = [ (tu.dt(att.date) +
                       tu.timedelta(days = int(i.dayofweek) - tu.dt(att.date).weekday(), hours=i.hour_from),
                       tu.dt(att.date) +
                       tu.timedelta(days = int(i.dayofweek) - tu.dt(att.date).weekday(), hours=i.hour_to + 24*(i.hour_to < i.hour_from)))
                     for i in  cont.turn_id.timesheet_id ]
            turns = filter(lambda (f,t):
                             f - tu.timedelta(hours=6) <= tu.dt(att.datetime) and
                             tu.dt(att.datetime) <= t + tu.timedelta(hours=6), turns)
            if len(turns) > 0:
                res[att.id] = tu.dt2s(turns[0][0])
            else:
                res[att.id] = False
        return res

    def _get_turn_end(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        conts = self._get_contract(cr, uid, ids, 'contract', None, context=context)
        items = conts.items()
        if len(items) == 0: return False
        att_ids, con_ids = tuple(map(list, zip(*items)))
        cons = self.pool.get('hr.contract').browse(cr, uid, con_ids)
        atts = self.pool.get('hr.attendance').browse(cr, uid, att_ids)
        for (att, cont) in zip(atts, cons):
            turns = [ (tu.dt(att.date) +
                       tu.timedelta(days = int(i.dayofweek) - tu.dt(att.date).weekday(),
                                    hours=i.hour_from),
                       tu.dt(att.date) +
                       tu.timedelta(days = int(i.dayofweek) - tu.dt(att.date).weekday(),
                                    hours=i.hour_to + 24*(i.hour_to < i.hour_from)))
                     for i in  cont.turn_id.timesheet_id ]
            turns = filter(lambda (f,t):
                             f - tu.timedelta(hours=6) <= tu.dt(att.datetime) and
                             tu.dt(att.datetime) <= t + tu.timedelta(hours=6), turns)
            if len(turns) > 0:
                res[att.id] = tu.dt2s(turns[0][1])
            else:
                res[att.id] = False
        return res

    def _get_turn_date(self, cr, uid, ids, field_name, arg, context=None):
        res = self._get_turn_start(cr, uid, ids, field_name, arg,
                                  context=context)
        if not res:
            return False

        for k in res:
            if res[k]:
                res[k] = tu.dt2s(
                    tu.datetime.combine(tu.dt(res[k]).date(), tu.time(0)))

        return res

    def _get_holidays(self, cr, uid, ids, field_name, arg, context=None):
        state_map = {
            'confirmed_holidays': 'confirm',
            'validated_holidays': 'validate',
            'refused_holidays':   'refuse',
        }
        if field_name in state_map:
            state = 'and state = \'%s\'' % state_map[field_name]
        else:
            state = ''
        _query_ = """
            SELECT
                A.id, H.id
            FROM
                hr_attendance as A
                LEFT OUTER JOIN
                hr_holidays as H
                ON
                (H.date_from, H.date_to) OVERLAPS (A.name, A.name) AND
                (A.employee_id = H.employee_id OR H.employee_id is Null)
            WHERE
                A.id in ( %s )
                %s
        """ % (",".join(map(str, ids)), state)
        cr.execute(_query_)
        res = dict(map(lambda i: (i, []), ids))
        for a, h in cr.fetchall():
            if h: res[a].append(h)
        return res

    def _get_has_holidays(self, cr, uid, ids, field_name, arg, context=None):
        state_map = {
            'has_confirmed_holidays': 'confirmed',
            'has_validated_holidays': 'validated',
            'has_refused_holidays':   'refused',
        }
        if field_name in state_map:
            field_name = '%s_holidays' % state_map[field_name]
        else:
            field_name = 'holidays'
        res = self._get_holidays(cr, uid, ids, field_name, arg,
                                 context=context)
        for k in res:
            res[k] = len(res[k])>0
        return res

    def _get_previous(self, cr, uid, ids, field_name, arg, context=None):
        _query_ = """
            SELECT
                A.id, P.id
            FROM
                hr_attendance as A
                LEFT JOIN
                hr_attendance as P
                ON A.employee_id = P.employee_id AND A.name > P.name
                LEFT OUTER JOIN
                hr_attendance as M
                ON  P.name < M.name
                AND A.employee_id = M.employee_id
                AND A.name > P.name AND A.name > M.name
            WHERE
                A.id in ( %s ) AND
                M.name is Null
        """ % ",".join(map(str, ids))
        cr.execute(_query_)
        return dict(cr.fetchall())

    def _get_next(self, cr, uid, ids, field_name, arg, context=None):
        _query_ = """
            SELECT
                A.id, P.id
            FROM
                hr_attendance as A
                LEFT JOIN
                hr_attendance as P
                ON A.employee_id = P.employee_id AND A.name < P.name
                LEFT OUTER JOIN
                hr_attendance as M
                ON  P.name > M.name
                AND A.employee_id = M.employee_id
                AND A.name < P.name AND A.name < M.name
            WHERE
                A.id in ( %s ) AND
                M.name is Null
            ORDER BY A.employee_id, A.name
        """ % ",".join(map(str, ids))
        cr.execute(_query_)
        return dict(cr.fetchall())

    def _get_date(self, cr, uid, ids, field_name, arg, context=None):
        res = map(lambda a: (a.id,
                             tu.dt2s(tu.datetime.combine(tu.dt(a.name).date(),tu.time(0)))),
            self.browse(cr, uid, ids))
        return dict(res)

    def _get_datetime(self, cr, uid, ids, field_name, arg, context=None):
        res = map(lambda a: (a.id, a.name),
            self.browse(cr, uid, ids))
        return dict(res)

    _columns = {
        'previous' : fields.function(_get_previous, type='one2one',
                                     obj='hr.attendance', method=True,
                                     string='Previous attendance'),
        'next' : fields.function(_get_next, type='one2one',
                                     obj='hr.attendance', method=True,
                                     string='Next attendance'),
        'holidays' : fields.function(_get_holidays, type='many2many',
                                     obj='hr.holidays', method=True,
                                     string='Holidays'),
        'confirmed_holidays' : fields.function(_get_holidays, type='many2many',
                                     obj='hr.holidays', method=True,
                                     string='Holidays'),
        'validated_holidays' : fields.function(_get_holidays, type='many2many',
                                     obj='hr.holidays', method=True,
                                     string='Validated Holidays'),
        'refused_holidays' : fields.function(_get_holidays, type='many2many',
                                     obj='hr.holidays', method=True,
                                     string='Refused Holidays'),
        'has_holidays' : fields.function(_get_holidays, type='bool',
                                     obj='hr.holidays', method=True,
                                     string='Has Holidays?'),
        'has_confirmed_holidays' : fields.function(_get_has_holidays,
                                                   type='bool',
                                     obj='hr.holidays', method=True,
                                     string='Has Confirmed Holidays?'),
        'has_validated_holidays' : fields.function(_get_has_holidays,
                                                   type='bool',
                                     obj='hr.holidays', method=True,
                                     string='Has Validated Holidays?'),
        'has_refused_holidays' : fields.function(_get_has_holidays, type='bool',
                                     obj='hr.holidays', method=True,
                                     string='Has Refused Holidays?'),
        'contract' : fields.function(_get_contract, type='one2one',
                                     obj='hr.contract', method=True,
                                     string='Contract'),
        'turn_date' : fields.function(_get_turn_date, type='datetime',
                                     method=True, string='Turn date'),
        'turn_start' : fields.function(_get_turn_start, type='datetime',
                                     method=True, string='Turn start'),
        'turn_end' : fields.function(_get_turn_end, type='datetime',
                                     method=True, string='Turn end'),
        'date' : fields.function(_get_date, type='datetime',
                                     method=True, string='Attendance date'),
        'datetime' : fields.function(_get_datetime, type='datetime',
                                     method=True, string='Attendance datetime'),
#        'journal_id': fields.many2one('hr.aa.journal', 'Journal',
#                ondelete="setnull", select=True),
    }
hr_attendance()

class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    _name = "hr.holidays"

    def onchange_hr_aa_const_or_null(self, cr, uid, ids, name, default, value):
        # I need setup the employee on an instance creation but I dont know how
        # to setup null.
        #val = {}
        #if value:
        #    val = { name: default }
        val = { name: default }
        return { 'value': val }

    def onchange_hr_aa_dates(self, cr, uid, ids, field,
                             date_from, date_to,
                             newdate_from, newdate_to):
        val = {}
        newdate_from = newdate_from or date_from
        newdate_to = newdate_to or date_to
        if newdate_to < date_from:
            newdate_to = date_from
        if date_to < newdate_from:
            newdate_from = date_to
        if newdate_from > newdate_to and field=='date_from':
            newdate_from = newdate_to
        if newdate_from > newdate_to and field=='date_to':
            newdate_to = newdate_from
        val['date_from'] = newdate_from
        val['date_to'] = newdate_to
        return { 'value': val }
hr_holidays()

class hr_journal_formula(osv.osv):
    _name = "hr.aa.journal.formula"
    _description = "Day Processor Function"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16,
            help="Used to get the value in other formulas"),
        'label' : fields.char('Label', size=16,
            help="Label used in reports. If null the value not visible."),
        'active': fields.boolean('Active'),
        'seq': fields.integer('Solve Sequence', required=True,
            help="Solve low values first"),
        'function' : fields.text('Function', required=True),
        'default' : fields.float('Default', required=True,
            help="First value without evaluation"),
    }
    _defaults = {
        'function': lambda *a: 'lambda journal: .0',
        'seq': lambda *a: 10,
        'default': lambda *a: .0,
    }
    _order = 'seq asc'
hr_journal_formula()

class hr_journal(osv.osv):
    def _get_turn_start(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for journal in self.browse(cr, uid, ids):
            if journal.turn_id:
		wd_l = [ str(tu.d(journal.date).weekday()), '' ]
                ts = filter(lambda i:
                                i.dayofweek in wd_l,
                                journal.turn_id.timesheet_id)
                if len(ts) == 1:
                    res[journal.id] = tu.dt2s(tu.d(journal.date) +
                                        tu.timedelta(hours=ts[0].hour_from))
                elif len(ts) > 1:
                    raise osv.except_osv(_('Error'), _('Overlaped turn for the journal %s.') % journal.name)
                else:
                    res[journal.id] = False
            else:
                res[journal.id] = False
        return res

    def _get_turn_end(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for journal in self.browse(cr, uid, ids):
            if journal.turn_id:
		wd_l = [ str(tu.d(journal.date).weekday()), '' ]
                ts = filter(lambda i:
                                i.dayofweek in wd_l,
                                journal.turn_id.timesheet_id)
                if len(ts) == 1:
                    res[journal.id] = tu.dt2s(tu.d(journal.date) + tu.timedelta(hours=ts[0].hour_to
                                                               + 24 * (ts[0].hour_from
                                                                       > ts[0].hour_to)))
                elif len(ts) > 1:
                    raise osv.except_osv(_('Error'), _('Overlaped turn for the journal %s.') % journal.name)
                else:
                    res[journal.id] = False
            else:
                res[journal.id] = False
        return res

    def _get_day_start(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        dtc = lambda sd: tu.dt(sd.sign_in_id.name)
        for day in self.browse(cr, uid, ids):
            if day.attendance_ids:
                res[day.id] = tu.dt2s(min(map(lambda i: tu.dt(i.name),
                                              day.attendance_ids)))
            else:
                res[day.id] = False
        return res

    def _get_day_end(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        dtc = lambda sd: tu.dt(sd.sign_out_id.name)
        for day in self.browse(cr, uid, ids):
            if day.attendance_ids:
                res[day.id] = tu.dt2s(max(map(lambda i: tu.dt(i.name),
                                              day.attendance_ids)))
            else:
                res[day.id] = False
        return res

    def _get_is_valid(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for day in self.browse(cr, uid, ids):
            v = True
            if day.attendance_ids:
                v = v and day.attendance_ids[0].action == 'sign_in'
                v = v and day.attendance_ids[-1].action == 'sign_out'
                v = v and all([day.attendance_ids[i].action != day.attendance_ids[i+1].action for i in range(len(day.attendance_ids)-1)])
            res[day.id] = v
        return res

    def _get_day_end(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        dtc = lambda sd: tu.dt(sd.sign_out_id.name)
        for day in self.browse(cr, uid, ids):
            if day.attendance_ids:
                res[day.id] = tu.dt2s(max(map(lambda i: tu.dt(i.name),
                                              day.attendance_ids)))
            else:
                res[day.id] = False
        return res


    def _date_overlaps(self, cr, uid, ids, date, context=None):
        res = {}
        for j in self.browse(cr, uid, ids):
            r = True
            r = r and tu.dt(j.turn_start) - tu.timedelta(hours=2) < date
            r = r and date < tu.dt(j.turn_end) + tu.timedelta(hours=2)
            res[j.id] = r
        return res

    def _date_range_overlaps(self, cr, uid, ids, date_from, date_to, context=None):
        res = {}
        for j in self.browse(cr, uid, ids):
            r = date_from < date_to and not (
                (date_to < tu.dt(j.turn_start)) or
                (tu.dt(j.turn_end) < date_from)
            )
            res[j.id] = r
        return res


    def _get_attendance(self, cr, uid, ids, field_name, arg, context=None):
        """
        Generate list of attendance associated to the this journal.
        """
        res = {}
	data = self.read(cr, uid, ids, ['employee_id', 'turn_start', 'turn_end'], context=context)
	delta = tu.timedelta(hours=2)
	for d in data:
            turn_start = d['turn_start']
            turn_end = d['turn_end']
            employee_id = d['employee_id'][0]
	    _id = d['id']
            if turn_start:
                sql_req= """
                SELECT A.id
                FROM hr_attendance as A
                WHERE
                  A.employee_id = %d AND
                  ('%s'::timestamp, '%s'::timestamp)
                  OVERLAPS
                  (A.name, A.name)
                ORDER BY A.name asc""" % (
                      employee_id,
                      tu.dt(turn_start) - delta,
                      tu.dt(turn_end) + delta
                  )
                cr.execute(sql_req)
                sql_res = cr.fetchall()

                if len(sql_res) > 0:
                    res[_id] = map(lambda (i,): i, sql_res)
                else:
                    res[_id] = []
        return res

    def _inv_attendance(self, cr, uid, ids, field_name, value, arg, context=None):
        """
        Store attendance from a journal. Assign employee id and set the correct
        datetime.
        """
        jou_id = ids
        for no_se, att_id, val in value:
            if val:
                # Who is the associated journal?
                if jou_id == 0:
                    if not isinstance(ids, int):
                        raise osv.except_osv(_('Error'),
                                             _('I expect process attendance just for one journal'))
                    jou_id = ids
                jou = self.browse(cr, uid, jou_id)

                # Check date if not out of turn time.
                if not jou._date_overlaps(tu.dt(val['name']))[jou.id]:
                    an = tu.datetime.combine(tu.d(jou.date).date(), tu.dt(val['name']).time())
                    if not jou._date_overlaps(an)[jou.id]:
                        an = tu.datetime.combine(tu.d(jou.date).date() + tu.timedelta(days=1), tu.dt(val['name']).time())
                    val['name'] = tu.dt2s(an)
                    if not (jou._date_overlaps(tu.dt(val['name']))):
                        raise osv.except_osv(_('Error'),
                                             _('Attendance don\'t belong to this journal'))

        # Sort entries
        att_ids = []
        values = []
        for no_se, att_id, val in value:
            if val:
                att_ids.append(att_id)
                values.append(val) 
        att_ids.sort()
        values.sort(key=lambda i: i['name'])
        attval = dict(zip(att_ids, values))

        # Store new or modification
        for att_id, val in zip(att_ids, values):
            if val:
                if att_id == 0:
                   val['employee_id'] = jou.employee_id.id
                   self.pool.get('hr.attendance').create(cr, uid, val)
                else:
                   self.pool.get('hr.attendance').write(cr, uid, att_id, val)

        # Delete entries
        for no_se, att_id, val in value:
            if not val:
                self.pool.get('hr.attendance').unlink(cr, uid, att_id)

    def _get_holidays(self, cr, uid, ids, field_name, arg, context=None):
        """
        Generate list of attendance associated to the this journal.
        """
        res = {}
	data = self.read(cr, uid, ids, ['employee_id', 'date', 'turn_start', 'turn_end'], context=context)
	for d in data:
            turn_start = d['turn_start']
            turn_end = d['turn_end']
            employee_id = d['employee_id'][0]
	    date = d['date']
	    _id = d['id']
            if turn_start:
                date_start, date_end = turn_start, turn_end
            else:
                date_start, date_end = date, tu.dt2s(tu.d(date) +
                                                         tu.timedelta(days=1))

            sql_req= """
            SELECT H.id AS func_id
            FROM hr_holidays as H
            WHERE
              (H.employee_id = %d OR H.employee_id is Null) AND
              (H.date_from, H.date_to) OVERLAPS
              ('%s'::timestamp, '%s'::timestamp)
            """ % (employee_id, date_start, date_end)
            cr.execute(sql_req)
            sql_res = cr.fetchall()

            if len(sql_res) > 0:
                res[_id] = map(lambda (i,): i, sql_res)
            else:
                res[_id] = []
        return res

    def _inv_holidays(self, cr, uid, ids, field_name, value, arg, context=None):
        """
        Store holidays from a journal. Assign employee id and set the correct
        datetime. Calculate number of days.
        """
        jou_id = ids
        for no_se, hol_id, val in value:
            # Who is the associated journal?
            if jou_id == 0:
                if not isinstance(ids, int):
                    raise osv.except_osv(_('Error'),
                                         _('I expect process holidays just for one journal'))
                jou_id = ids
            jou = self.browse(cr, uid, jou_id)

            # Employee in holiday must be the same employee
            # or none
            if not (not val['employee_id'] or
                    jou.employee_id.id == val['employee_id']):
                raise osv.except_osv(_('Error'),
                                     _('You must assign holiday to the same employee of the journal'))

            # Check if range date if not out of turn range.
            if not ( jou._date_range_overlaps(tu.dt(val['date_from']),
                                              tu.dt(val['date_to']))[jou.id] ):
                raise osv.except_osv(_('Error'),
                                     _('You must define the holiday date range witch overlaps the turn range'))

            # Calculate number of days
            val['number_of_days'] = max([(tu.dt(val['date_to']) -
                                          tu.dt(val['date_from'])).days, 1])

            if hol_id != 0:
                self.pool.get('hr.holidays').write(cr, uid, hol_id, val)
            else:
                self.pool.get('hr.holidays').create(cr, uid, val)

    _name = "hr.aa.journal"
    _description ="Attendance of a day"
    _columns = {
        'name': fields.char("Name", size=64, required=True,
                readonly=True),
        'date' : fields.date("Date", required=True, select=True,
                readonly=True),
        'employee_id': fields.many2one("hr.employee", "Employee",
                required=True, select=True,
                readonly=True),
        'turn_id': fields.many2one("hr.timesheet.group", "Turn",
                required=True, select=True,
                readonly=True, states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one("hr.department", "Department",
                required=True, select=True,
                readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
                    ('draft','Draft'),
                    ('confirmed','Confirmed'),
                ],'State', select=True, readonly=True),
        'note': fields.text('Note', # Nota o comentario
                readonly=True, states={'draft': [('readonly', False)]}),
        'turn_start':  fields.function(_get_turn_start, type='datetime',
                                      method=True, string='Start of the turn'),
        'turn_end':  fields.function(_get_turn_end, type='datetime', method=True,
                                    string='End of the turn'),
        'day_start':  fields.function(_get_day_start, type='datetime',
                                      method=True, string='Start of the day'),
        'day_end':  fields.function(_get_day_end, type='datetime', method=True,
                                    string='End of the day'),
        'contract_hours':  fields.float('Contract time'),
        'holiday_ids': fields.function(_get_holidays,
                                       fnct_inv=_inv_holidays,
                                       type='one2many',
                                       obj='hr.holidays', method=True,
                                       string='Holidays'),
        'attendance_ids': fields.function(_get_attendance,
                                          fnct_inv=_inv_attendance,
                                          type='one2many',
                                          obj='hr.attendance', method=True,
                                          string='Attendances'),
        'value_ids': fields.one2many('hr.aa.journal.value', 'journal_id', 'Day values'),
        'is_valid':  fields.function(_get_is_valid, type='boolean', method=True,
                                    string='Is Valid?'),
    }
    _defaults = {
        'state': lambda *a: 'draft', # TODO: Cancel state is necessary
    }
    _sql_constraints = [
        ('employee_date', 'UNIQUE (employee_id, date)', 'Employee and date must be unique' )
    ]
    _order = 'date desc'
    _value_prefix = 'v_'

    def read(self, cr, uid, ids, fields_to_read=None, context=None, load='_classic_read'):
        """
        Read an instance of Journal. Append values to properties.
        """
        result = super(hr_journal, self).read(cr, uid, ids, fields_to_read, context, load)

        # Solo procesamos si alguien lo pide
        vp = self._value_prefix
	lvp = len(vp)
	if (fields_to_read and
            not filter(lambda i: vp == i[:lvp], fields_to_read) and
            not 'visibles' in fields_to_read):
            return result

        pool_value = self.pool.get('hr.aa.journal.value')
        pool_formula = self.pool.get('hr.aa.journal.formula')
        formula_ids = pool_formula.search(cr, uid, [], context=context)
        formulas = pool_formula.browse(cr, uid, formula_ids, context=context)

        islist = isinstance(result, list)

        if not islist:
            result=[result]

        for res in result:
            value_ids = pool_value.search(cr, uid, [('journal_id', '=', res['id'])])
            values = pool_value.browse(cr, uid, value_ids, context=context)

            visibles = []
            for formula in formulas:
                n = vp + formula.code
                res[n] = formula.default
                if formula.label != '': visibles.append(n)

            for value in values:
                n = vp + value.formula_id.code
                if n in res: res[n] = value.value

            res['visibles'] = visibles

        if not islist:
            result=result[0]

        return result

    def write(self, cr, uid, ids, vals, context=None):
        """
        Write an instance of Journal. Write values to properties too.
        """
        vals_new = vals.copy()
        pool_journal = self.pool.get('hr.aa.journal')
        pool_value = self.pool.get('hr.aa.journal.value')
        pool_formula = self.pool.get('hr.aa.journal.formula')
        vp = self._value_prefix

        for journal in self.browse(cr, uid, ids, context=context):
            journal_id = journal.id
            res = {}
            for val in vals:
                if not val[:len(vp)]==vp:
                    continue
                code = val[len(vp):]
                formula_ids = pool_formula.search(cr, uid,
                                                [('code', '=', code)],
                                                context=context)
                if len(formula_ids)!=1:
                    continue
                value_ids = pool_value.search(cr, uid,
                                             [('formula_id', '=',
                                               formula_ids[0]),
                                              ('journal_id', '=',
                                               journal_id),
                                             ],
                                             context=context)
                if len(value_ids) == 0:
                    value_ids = [pool_value.create(cr, uid, {
                        'name': journal.name,
                        'journal_id':journal_id,
                        'formula_id':formula_ids[0],
                    }) ]
                vals2 = { 'value': vals[val] }
                pool_value.write(cr, uid, value_ids, vals2, context=context)

        vals = dict(filter(lambda (k,v): k[:len(vp)] != vp, vals.items()))
        res = super(hr_journal, self).write(cr, uid, ids, vals, context)
        return res

    def values(self, cr, uid, ids, context=None):
        res = dict([ (i, {}) for i in ids ])
        for day in self.browse(cr, uid, ids, context=context):
            d = {}
            for value in day.value_ids:
                d[value.formula_id.code] = value.value
            res[day.id] = d.copy()
        return res

    def create(self, cr, uid, vals, context=None):
        """
        Create a new instance of journal
        """
        if 'name' not in vals:
            vals['name'] = '%i - %s' % (vals['employee_id'], time.strftime('%Y/%m/%d'))

        journal_id = super(hr_journal, self).create(cr, uid, vals, context=context)

        self.fill(cr, uid, [journal_id])

        return journal_id

    def fill(self, cr, uid, ids, context=None):
        """
        Fill journal of values
        """
        pool_value = self.pool.get('hr.aa.journal.value')
        pool_formula = self.pool.get('hr.aa.journal.formula')

        vp = self._value_prefix

        for journal in self.browse(cr, uid, ids):
            formulas = [ f for f in pool_formula.browse(cr, uid, pool_formula.search(cr, uid, []))
                         if f not in [ i.formula_id for i in journal.value_ids ]]

            for formula in formulas:
                n = pool_value.create(cr, uid, {
                    'name': '%s - %s' % (journal.name, formula.code),
                    'journal_id': journal.id,
                    'formula_id': formula.id,
                    'value': formula.default,
                })

    def fields_get(self, cr, uid, fields=None, context=None, read_access=True):
        """
        Recalculate fields
        """
        res = super(hr_journal, self).fields_get(cr, uid, fields, context)
        pool_formula = self.pool.get('hr.aa.journal.formula')
        formula_ids = pool_formula.search(cr, uid, [])
        formulas = pool_formula.browse(cr, uid, formula_ids, context=context)
        vp = self._value_prefix
        for formula in formulas:
            res[vp+formula.code] = {'string': formula.label, 'type': 'float'}
        return res

    def compute(self, cr, uid, ids, context=None):
        """
        Calcula las horas según los bloques de horas asociadas y el contrato
        actual.
        Tambien computa las reglas.
        """
        pool_val = self.pool.get('hr.aa.journal.value')
        pool_att = self.pool.get('hr.attendance')
        value_ids = []
        attendance_ids = []

        for journal in self.browse(cr, uid, ids, context=context):
            if journal.state == 'draft':
                journal.fill()
                value_ids = value_ids + [ i.id for i in journal.value_ids ]
                attendance_ids = attendance_ids + [ i.id for i in
                                               journal.attendance_ids ]

        pool_att.compute_reason_rules(cr, uid, attendance_ids)
        pool_val.compute(cr, uid, value_ids)

    def validate(self, cr, uid, ids, context=None):
        return True

    def confirm(self, cr, uid, ids, context=None):
        if self.validate(cr, uid, ids, context):
            self.write(cr, uid, ids, {
            'state':'confirmed',
            })
            return True
        else:
            return False

    def unconfirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state':'draft',
            })
        return True

    def button_compute(self, cr, uid, ids, context=None):
        return self.compute(cr, uid, ids, context=context)

    def build(self, cr, uid, date_from, date_to, context=None):
        emp_pool = self.pool.get('hr.employee')
        con_pool = self.pool.get('hr.contract')
        journal_ids = []
        for time in tu.daterange(tu.dt(date_from), tu.dt(date_to) + tu.timedelta(days=1)):
            journal_date = tu.dt2s(time)
            emp_ids = emp_pool.search(cr, uid, [], context=context)
            con_ids = emp_pool.get_valid_contract(cr, uid, emp_ids, time)

            for (emp_id, con_id) in con_ids.items():
                emp = emp_pool.browse(cr, uid, emp_id, context=context)
                con = con_pool.browse(cr, uid, con_id, context=context)

                contract_hours = (
                    str(time.weekday()) in [ ts.dayofweek for ts in
                                                con.turn_id.timesheet_id ]
                    ) * con.working_hours_per_day

                journal = {
                    'name': emp.name + time.strftime(' (%d/%m/%Y)'),
                    'date': journal_date,
                    'employee_id': emp_id,
                    'turn_id': con.turn_id.id,
                    'department_id': con.department_id.id,
                    'contract_hours': contract_hours,
                }
                jids = self.search(cr, uid, [
                    ('employee_id', '=', journal['employee_id']),
                    ('date', '=', journal['date']),
                ])
                if len(jids) == 0:
                    journal_ids.append(self.create(cr, uid, journal, context=context))
                else:
                    logger.notifyChannel('hr.aa.journal',
                                 netsvc.LOG_INFO,
                                 'Yet exists journal \'%s\'' %
                                 journal['name'])

        self.compute(cr, uid, journal_ids, context=context)
        return len(journal_ids)

hr_journal()

class hr_journal_value(osv.osv):
    _name = "hr.aa.journal.value"
    _description = "Journal Value"
    _columns = {
        'name': fields.char('Value Name', size=32, required=True),
        'journal_id': fields.many2one('hr.aa.journal', 'Journal',
                                      required=True, ondelete="cascade",
                                      select=True),
        'formula_id' : fields.many2one('hr.aa.journal.formula', 'Function type', required=True, ondelete='cascade'),
        'value': fields.float('Value'),
    }

    def compute(self, cr, uid, ids, context=None):
        #
        # Define classes and functions: date, datetime, timedelta, time, dt, d
        #
        _r_globals = {
            'date': tu.date,
            'datetime': tu.datetime,
            'timedelta': tu.timedelta,
            'time': tu.time,
            'total_hours': tu.total_hours,
            'total_seconds': tu.total_seconds,
            'dt': tu.dt,
            'd': tu.d,
            'presition': lambda v, p: round(v/p)*p,
        }

        pool_form = self.pool.get('hr.aa.journal.formula')
        form_ids = pool_form.search(cr, uid, [], context=context)

        f = {}
        for form in pool_form.browse(cr, uid, form_ids):
            code = form.function.strip()
            logger.notifyChannel('hr.aa.journal.value',
                                 netsvc.LOG_DEBUG,
                                 'Compiling (%s) %s' %
                                 (form.name, code))
            f[form.id] = eval(code, _r_globals)

        for value in sorted(self.browse(cr, uid, ids,
                                        context=context),
                           key=lambda l: l.formula_id.seq):
            j = value.journal_id
            J = Interface(cr, uid, self.pool, j.id, j._table_name)
            if value.formula_id.label and value.formula_id.label[:2] == 'd_':
                import readline
                import sys
                print "--"
                print "-- Evaluando funcion '%s' en elemento J=<'%s'>" % (value.formula_id.label, J.name)
                print "--"
                _r_globals['J'] = J
                _r_globals['f'] = f[value.formula_id.id]
                _r_globals['code'] = value.formula_id.function.strip()
                while True:
                    cmd = raw_input(">> ")
                    if cmd == 'q': break
                    try:
                       print eval(cmd, _r_globals)
                    except:
                       e = sys.exc_info()[1]
                       print e
                del _r_globals['J']
                del _r_globals['f']
                del _r_globals['code']

            v = f[value.formula_id.id](J)
            logger.notifyChannel('hr.aa.journal.value',
                                 netsvc.LOG_DEBUG,
                                 'Evaluating %s=%s' %
                                 (value.formula_id.name, v))
            self.write(cr, uid, value.id, { 'value': v })
hr_journal_value()

# TODO: Check if a code is a valid variable name

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
