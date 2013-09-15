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


from osv import fields, osv
import netsvc
import timeutils as tu
import time
from interface import Interface

logger = netsvc.Logger()

class hr_aa_payroll(osv.osv):
    _name = "hr.aa.payroll"
    _description = "Payroll Document"
    _columns = {
        "name": fields.char("Name", size=64, required=True),
        "date_from": fields.date("Date from", required=True),
        "date_to": fields.date("Date to", required=True),
        'state': fields.selection([
                    ('draft','Draft'),
                    ('confirmed','Confirmed'),
                ],'State', select=True, readonly=True),
        "note": fields.text("Note"),
        "line_ids": fields.one2many("hr.aa.payroll.line", "payroll_id", "Lines"),
    }
    _defaults = {
        'state': lambda *a: 'draft', # TODO: Cancel state is necessary
    }

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

    def build(self, cr, uid, date_from, date_to, emp_ids=[], context=None):
        pool_emp = self.pool.get('hr.employee')
        pool_line = self.pool.get('hr.aa.payroll.line')
        pool_con = self.pool.get('hr.contract')

        pr_name = "%s - %s" % (date_from, date_to)
        pr_id = self.create(cr, uid, {
            'name': pr_name,
            'date_from': date_from,
            'date_to': date_to,
        })

        emps = pool_emp.browse(cr, uid, emp_ids)
        for emp in emps:
            con_id = emp.get_valid_contract(tu.d(date_from))[emp.id]
            con = pool_con.browse(cr, uid, con_id, context=context)
            pool_line.create(cr, uid, {
                'name': "%s (%s)" % (emp.name, pr_name),
                'employee_id': emp.id,
                'payroll_id': pr_id,
                'wage_type_id': con.wage_type_id.id,
                'wage': con.wage,
            })

        return pr_id

    def compute(self, cr, uid, ids, context=None):
        lines_to_compute = []
        for payroll in self.browse(cr, uid, ids, context=context):
            if payroll.state == 'draft':
                self.pool.get('hr.aa.journal').build(cr, uid,
                                                tu.dt2s(tu.d(payroll.date_from)),
                                                tu.dt2s(tu.d(payroll.date_to)),
                                                context=context)
                lines_to_compute += [ l.id for l in payroll.line_ids ]
	import cProfile
	cProfile.runctx('self.pool.get("hr.aa.payroll.line").compute(cr, uid, lines_to_compute)',
			{'self': self, 'cr':cr, 'uid':uid, 'lines_to_compute': lines_to_compute},
			None,
			'/tmp/compute.pstats')
	return True
hr_aa_payroll()

class hr_aa_payroll_formula(osv.osv):
    _name = "hr.aa.payroll.formula"
    _description = ""
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16,
            help='Used to get the value in other formulas'),
        'label' : fields.char('Label', size=16,
            help='Label used in reports. If null the value not visible.'),
        'active': fields.boolean('Active'),
        'seq': fields.integer('Priority', required=True,
            help='Solve first low values'),
        'formula' : fields.text('Formula', required=True),
        'default' : fields.float('Default', required=True,
            help='First value without evaluation'),
    }
    _defaults = {
        "formula": lambda *a: "lambda day: 0",
        "seq": lambda *a: 10,
    }
    _order = "seq asc"
hr_aa_payroll_formula()

class hr_aa_payroll_line(osv.osv):
    _name = "hr.aa.payroll.line"
    _description = "Payroll Line"
    _columns = {
        "name": fields.char("Name", size=64, required=True),
        "employee_id": fields.many2one("hr.employee", "Employee", required=True),
        "payroll_id": fields.many2one("hr.aa.payroll", "Payroll", required=True,
                                      ondelete="cascade"),
        # start of Dangerous lines
        "wage_type_id": fields.many2one("hr.contract.wage.type", "Wage Type"),
        "wage": fields.float("Wage"),
        # end of Dangerous lines
        "value_ids": fields.one2many("hr.aa.payroll.value", "line_id", "Values"),
        "note": fields.char("Note", size=128),
    }
    _defaults = {
        "name": lambda self, cr, uid, context: "%i" % context['active_id'],
    }
    _value_prefix = 'v_'

    def read(self, cr, uid, ids, fields_to_read=None, context=None, load='_classic_read'):
        """
        Read an instance of Payroll Line. Append values to properties.
        """
        result = super(hr_aa_payroll_line, self).read(cr, uid, ids, fields_to_read, context, load)
        pool_value = self.pool.get('hr.aa.payroll.value')
        pool_formula = self.pool.get('hr.aa.payroll.formula')
        formula_ids = pool_formula.search(cr, uid, [], context=context)
        formulas = pool_formula.browse(cr, uid, formula_ids, context=context)
        vp = self._value_prefix

        if not isinstance(result, list):
            result=[result]

        for res in result:
            value_ids = pool_value.search(cr, uid, [('line_id', '=', res['id'])])
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
        return result

    def write(self, cr, uid, ids, vals, context=None):
        """
        Write an instance of Payroll Line. Write values to properties too.
        """
        vals_new = vals.copy()
        pool_line = self.pool.get('hr.aa.payroll.line')
        pool_value = self.pool.get('hr.aa.payroll.value')
        pool_formula = self.pool.get('hr.aa.payroll.formula')
        vp = self._value_prefix

        for line in self.browse(cr, uid, ids, context=context):
            line_id = line.id
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
                                              ('line_id', '=',
                                               line_id),
                                             ],
                                             context=context)
                if len(value_ids) == 0:
                    value_ids = [pool_value.create(cr, uid, {
                        'name': line.name,
                        'line_id':line_id,
                        'formula_id':formula_ids[0],
                    }) ]
                vals2 = { 'value': vals[val] }
                pool_value.write(cr, uid, value_ids, vals2, context=context)
        vals = dict(filter(lambda (k,v): k[:len(vp)] != vp, vals.items()))
        res = super(hr_aa_payroll_line, self).write(cr, uid, ids, vals, context)
        return res

    def create(self, cr, uid, vals, context=None):
        pool_value = self.pool.get('hr.aa.payroll.value')
        pool_formula = self.pool.get('hr.aa.payroll.formula')
        vp = self._value_prefix

        svals = dict(filter(lambda (k,v): k[:len(vp)] != vp, vals.items()))
        if 'name' not in svals:
            svals['name'] = '%i - %s' % (vals['employee_id'], time.strftime('%Y/%m/%d'))
        line_id = super(hr_aa_payroll_line, self).create(cr, uid, svals, context=context)
        for val in dict(filter(lambda (k,v): k[:len(vp)] == vp, vals.items())):
            formula_ids = pool_formula.search(cr, uid,
                                            [('code', '=', val[len(vp):])],
                                            context=context)
            if len(formula_ids)!=1:
                continue

            value_ids = [pool_value.create(cr, uid, {
                'name': '%s - %s' % (svals['name'], formula_ids[0]),
                'line_id':line_id,
                'formula_id':formula_ids[0],
                'value': vals[val],
            }) ]
        return line_id

    def fields_get(self, cr, uid, fields=None, context=None, read_access=True):
        result = super(hr_aa_payroll_line, self).fields_get(cr, uid, fields, context)
        pool_formula = self.pool.get('hr.aa.payroll.formula')
        formula_ids = pool_formula.search(cr, uid, [])
        formulas = pool_formula.browse(cr, uid, formula_ids, context=context)
        vp = self._value_prefix
        res = {}
        for formula in formulas:
            res[vp + formula.code] = {'string': formula.label, 'type': 'float'}
        result.update(res)
        return result

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False):
        result = super(hr_aa_payroll_line, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar)
        pool_formula = self.pool.get('hr.aa.payroll.formula')
        formula_ids = pool_formula.search(cr, uid, [('label', '!=', '')])
        formulas = pool_formula.browse(cr, uid, formula_ids, context=context)
        cols = ['employee_id', 'wage_type_id', 'note']
        xml = '<%s editable="bottom" string="Payroll line">' % (view_type,)
        xml += '<field name="employee_id" expand="1"/>'
        xml += '<field name="wage_type_id"/>'
        for formula in formulas:
            xml += '<field name="%s"/>' % (self._value_prefix + formula.code)
        xml += '<field name="note" expand="1"/>'
        xml += '</%s>' % (view_type,)
        result['arch'] = xml
        result['fields'] = self.fields_get(cr, uid, cols, context)
        return result

    def values(self, cr, uid, ids, context=None):
        res = dict([ (i, {}) for i in ids ])
        for line in self.browse(cr, uid, ids, context=context):
            d = {}
            for value in line.value_ids:
                d[value.formula_id.code] = value.value
            res[line.id] = d.copy()
        return res

    def create_line_values(self, cr, uid, ids, context=None):
        """
        Create line values and associate then to payroll
        """
        pool_for = self.pool.get('hr.aa.payroll.formula')
        pool_val = self.pool.get('hr.aa.payroll.value')
        for line in self.browse(cr, uid, ids, context=context):
            for_ids = pool_for.search(cr, uid,
                                      [ ('name', 'not in',
                                         [ l.formula_id.name
                                          for l in line.value_ids]) ],
                                      context=context)
            val = []
            for form in pool_for.browse(cr, uid, for_ids, context=context):
                val.append(pool_val.create(cr, uid, {
                    'name': "%s - %s" % (line.name, form.name),
                    'line_id': line.id,
                    'formula_id': form.id,
                }, context=context))
        return True

    def compute(self, cr, uid, ids, context=None):
        """
        """
        values_to_compute = []
        for line in self.browse(cr, uid, ids, context=context):
                line.create_line_values()
                values_to_compute += [ v.id for v in line.value_ids ]
	self.pool.get("hr.aa.payroll.value").compute(cr, uid, values_to_compute)
        return True
hr_aa_payroll_line()

class hr_aa_payroll_value(osv.osv):
    _name = "hr.aa.payroll.value"
    _description = ""
    _columns = {
        "name": fields.char("Name", size=64, required=True),
        "line_id": fields.many2one("hr.aa.payroll.line", "Line", ondelete="cascade", required=True),
        "formula_id" : fields.many2one("hr.aa.payroll.formula", "Formula type", required=True),
        "value": fields.float("Value"),
    }
    _defaults = {
        "name": lambda self, cr, uid, context: "%i" % context['active_id'],
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

        pool_journal = self.pool.get('hr.aa.journal')
        pool_form = self.pool.get('hr.aa.payroll.formula')
        form_ids = pool_form.search(cr, uid, [], context=context)

        f = {}
        for form in pool_form.browse(cr, uid, form_ids):
            code = form.formula.strip()
            logger.notifyChannel('hr.aa.journal.value',
                                 netsvc.LOG_DEBUG,
                                 'Compiling (%s) %s' %
                                 (form.name, code))
            f[form.id] = eval(code, _r_globals)

        logger.notifyChannel('hr.aa.payroll_value',
                                 netsvc.LOG_INFO,
                                 'Empezando el calculo de formulas')
	cache = {}
        for value in sorted(self.browse(cr, uid, ids, context=context),
                            key=lambda v: v.formula_id.seq):
            line_id = value.line_id
	    payroll_id = line_id.payroll_id
	    employee_id = line_id.employee_id.id
	    date_from = payroll_id.date_from
	    date_to = payroll_id.date_to

	    if employee_id in cache and date_from in cache[employee_id] and date_to in cache[employee_id][date_from]:
                J = cache[employee_id][date_from][date_to]
                logger.notifyChannel('hr.aa.payroll_value',
                                 netsvc.LOG_DEBUG,
                                 'Hit %s,%s,%s' %
                                 (employee_id, date_from, date_to))
            else:
                logger.notifyChannel('hr.aa.payroll_value',
                                 netsvc.LOG_DEBUG,
                                 'Miss %s,%s,%s' %
                                 (employee_id, date_from, date_to))
                journal_ids = pool_journal.search(cr, uid, [
                    ('employee_id', '=', line_id.employee_id.id),
                    ('date', '>=', payroll_id.date_from),
                    ('date', '<=', payroll_id.date_to),
                ], context=context) # TODO: Los journals deben ser validados
                journals = pool_journal.browse(cr, uid, journal_ids, context=context)
                J = map(lambda (i,t): Interface(cr, uid, self.pool, i, t), 
                    [ (j.id, j._table_name) for j in journals ])
		if employee_id not in cache:
                    cache[employee_id] = { date_from: { date_to: J } }
		elif date_from not in cache[employee_id]:
                    cache[employee_id][date_from] = { date_to: J }
		else:
                    cache[employee_id][date_from][date_to] = J

            L = Interface(cr, uid, self.pool, value.line_id.id,
                          value.line_id._table_name)
            v = f[value.formula_id.id](L, J)
            logger.notifyChannel('hr.aa.payroll_value',
                                 netsvc.LOG_DEBUG,
                                 'Evaluating %s=%s' %
                                 (value.formula_id.name, v))
            self.write(cr, uid, value.id, { 'value': v })
        return True
hr_aa_payroll_value()

# TODO: Check if a code is a valid variable name
# TODO: Append list of visible values
# TODO: Append formula defaults

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

