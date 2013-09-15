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

logger = netsvc.Logger()

_rule_help = """Must be a lambda function with one parameter.
This example calc if the employee sing in at time:

    lambda att: lambda att: ( turn_start and turn_end and turn_start -
    timedelta(hours=1) < dt(att.name) and dt(att.name) < turn_start + timedelta(minutes=15))

The input of the lambda function is the attendance to check.

The following functions are available:

    dt: convert a string to datetime.
    d: convert a string to date.

And the following objetcs are available:

    timedelta: A delta of time
    date:      A date, without hour, minutes and seconds.
    datetime:  A date, with hour, minutes and seconds.
    time:      Just a time.

Following properties are availables for att:

    att.date:                   The date of the attendance.
    att.datetime:               The datetime of the attendance.
    att.action:                 The action of the attendance.
    att.turn_date:              The date associated to the enabled turn.
    att.turn_start:             The time when the turn start.
    att.turn_end:               The time when the turn end.
    att.previus:                The previuos attendance.
    att.next:                   The next attendance.
    att.has_confirmed_holidays: The employee has a request for holiday.
    att.has_refused_holidays:   The employee has a refused holiday.
    att.has_validated_holidays: The employee has a validated holiday.
    att.has_canceled_holidays:  The employee has a canceled holiday.
"""

class hr_action_reason_rule(osv.osv):
    _name = "hr.aa.action_reason_rule"
    _description = "Action Reason Rule"
    _columns = {
        'name' : fields.char("Name", size=64, required=True),
        'active': fields.boolean('Active'),
        'seq': fields.integer('Priority', required=True, help='Low values have'
                             ' more priority'),
        'rule' : fields.text("Rule", required=True, help=_rule_help),
        'action': fields.many2one('hr.action.reason', 'Action Reason',
                                  select=True),
    }
    _defaults = {
        'rule': lambda *a: 'lambda a: False',
        'seq': lambda *a: 10,
    }
    _sql_constraints = [
        ('rule_name', 'UNIQUE (name)', 'The name of the rule must be unique' )
    ]
    _order = 'seq desc'

    def compute(self, cr, uid, ids, att_ids, context=None):
        """
        Compute rules in to an attendance list
        """
        att_pool = self.pool.get('hr.attendance')
        con_pool = self.pool.get('hr.contract')
        hol_pool = self.pool.get('hr.holidays')
        att_ids = att_pool.search(cr,uid,[('id', 'in', att_ids)],
                                  order='name asc')

        # TODO: Compile rules before iterate over attendances
        for att in att_pool.browse(cr,uid,att_ids,context=context):
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
            }


            logger.notifyChannel('hr.aa.action_reason_rule', netsvc.LOG_DEBUG,
                                 'Attendance to check %s (%s) with turn %s - %s' % 
                                 (att.name, att.action,
                                  att.turn_start, att.turn_end))

            action = False
            for rule in [ r for r in self.browse(cr, uid, ids) if
                         r.action.action_type == att.action ]:
                code = rule.rule.strip()
                logger.notifyChannel('hr.aa.action_reason_rule',
                                     netsvc.LOG_DEBUG,
                                     'Compiling (%s) %s' %
                                     (rule.name, code))
                f = eval(code, _r_globals)
                A = Interface(cr, uid, self.pool, att.id, att._table_name)
                v = f(A)
                logger.notifyChannel('hr.aa.action_reason_rule',
                                     netsvc.LOG_DEBUG,
                                     'Evaluating %s=%s' %
                                     (rule.name, v))
                if att.action == rule.action.action_type and v:
                    action = rule.action

            if action:
                logger.notifyChannel('hr.aa.action_reason_rule', netsvc.LOG_DEBUG,
                                 'Selection %s' % action.name)
                att_pool.write(cr, uid, att.id, { 'action_desc': action.id })
hr_action_reason_rule()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _name = "hr.attendance"
    def compute_reason_rules(self, cr, uid, ids, context=None):
        rule_pool = self.pool.get('hr.aa.action_reason_rule')
        rule_ids = rule_pool.search(cr, uid,[],context=context)
        rule_pool.compute(cr, uid, rule_ids, ids, context=context)
hr_attendance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
