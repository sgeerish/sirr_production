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

from .. import timeutils as tu
from types import NoneType
import pooler
from tools.translate import _

from report.interface import report_rml

class report_custom(report_rml):
    def _xml_columns(self, cr, uid, context=None):
        pool_formula = pooler.get_pool(cr.dbname).get('hr.aa.payroll.formula')

        formula_ids = pool_formula.search(cr, uid, [('label', '!=', '')],
                                          context=context)
        formulas = pool_formula.browse(cr, uid, formula_ids, context=context)
        w = '%.2fcm' % (21.5/len(formulas))
        widths = ['1cm','2.5cm','1.5cm'] + [w]*len(formulas) + ['2.5cm']
        xml =  '    <columns>\n'
        xml += '        <widths>%s</widths>\n' % ','.join(widths)
        xml += '        <column id="employee_id">%s</column>\n' % _('Id')
        xml += '        <column id="employee">%s</column>\n' % _('Employee')
        xml += '        <column id="condition">%s</column>\n' % _('Wage Type')
        for formula in formulas:
            xml += '        <column id="value_%s">%s</column>\n' % \
                    (formula.code, formula.label)
        xml += '        <column id="note">%s</column>\n' % _('Note')
        xml += '    </columns>\n'
        return xml

    def _xml_lines(self, cr, uid, payroll, context=None):
        xml =  '    <lines>\n'
        for line in payroll.line_ids:
            xml += '        <line id="%i">\n' % line.id
            xml += '            <field id="employee_id">%s</field>\n' % line.employee_id.otherid
            xml += '            <field id="employee">%s</field>\n' % line.employee_id.name
            xml += '            <field id="condition">%s</field>\n' % line.wage_type_id.name
            for value in line.value_ids:
                if not value.formula_id.label: continue
                xml += '            <field id="value_%s">%.2f</field>\n' % (value.formula_id.code, value.value)
            xml += '            <field id="note">%s</field>\n' % (line.note or '')
            xml += '        </line>\n'
        xml += '    </lines>\n'
        return xml

    def create_xml(self, cr, uid, ids, data, context=None):
        pool_payroll = pooler.get_pool(cr.dbname).get('hr.aa.payroll')

        xml_columns = self._xml_columns(cr, uid, context=None)

        payrolls = pool_payroll.browse(cr, uid, ids)
        xml = '<?xml version="1.0" encoding="UTF-8" ?>\n'
        xml += '<report>\n'
        xml += '<date>%s</date>\n' % tu.datetime.now().strftime(
            '%A, %d %B %Y, %H:%M').decode('utf8')
        for payroll in payrolls:
            xml += '<payroll>\n'
            xml += '   <name>%s</name>\n' % payroll.name
            xml += '   <date_from>%s</date_from>\n' % \
                    tu.d(payroll.date_from).strftime('%d/%m/%Y')
            xml += '   <date_to>%s</date_to>\n' % \
                    tu.d(payroll.date_to).strftime('%d/%m/%Y')
            xml += '   <state>%s</state>\n' % payroll.state
            xml += xml_columns
            xml += self._xml_lines(cr, uid, payroll)
            xml += '   <note>%s</note>\n' % (payroll.note or '')
            xml += '</payroll>\n'
        xml += '</report>\n'

        import codecs
        f = codecs.open('/tmp/test.payroll.xml', 'w', encoding='utf8')
        f.write(xml)
        f.close()

        return xml

report_custom('report.hr.aa.payroll_print',
              'hr.aa.payroll',
              '',
              'addons/hr_attendance_analysis/report/payroll_report.xsl')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
