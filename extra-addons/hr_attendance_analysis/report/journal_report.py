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
import time
import pooler
import datetime
from report import report_sxw
from types import NoneType
import rml_parse

from report.interface import report_rml
from report.interface import toxml

class report_custom(report_rml):

    def gen_xml_employee(self, cr, uid, ids, context=None):
        pool_employee = self.pool.get('hr.employee')
        for employee in pool_employee.browse(cr, uid, ids, context=context):
            xml = u'<employee>\n'
            data = employee.read()[0]
            self.gen_xml_fields(data.keys())
            for i in [ (n,v,n) for n,v in data.items() if v ]:
                xml += ' <%s>%s</%s>\n' % i
            xml += '</employee>\n'
        return xml

    def gen_xml_fields(self, keys):
        if self.xml_fields: return

        xml = u'<labels>\n'
        for key in keys:
            xml += ' <label>%s</label>\n' % key
        xml += '</labels>\n'

        self.xml_fields = xml
        return

    def gen_xml_journals(self, cr, uid, ids, context=None):
        pool_journal = self.pool.get('hr.aa.journal')
        pool_att = self.pool.get('hr.attendance')
        pool_hol = self.pool.get('hr.holidays')

        fields = pool_journal.fields_get(cr, uid)

        if len(ids) == 0:
            return ''

        xml = u'<journals>\n'
        sums = {}

        for journal in pool_journal.browse(cr, uid, ids, context=context):
            data = journal.read()[0]
            self.gen_xml_fields(data.keys())
            xml += '  <journal>\n'
            for n,v in data.items():
                if not n in fields or v == False:
                    continue
                datatype = fields[n]['type']
                if datatype == 'many2one':
                    xml += '   <%s>%s</%s>\n' % (n,v[1],n)
                elif datatype == 'float':
                    xml += '   <%s>%7.2f</%s>\n' % (n,v,n)
                    if n not in sums: 
                        sums[n] = v
                    else:
                        sums[n] += v
                elif datatype == 'char':
                    xml += '   <%s>%s</%s>\n' % (n,v,n)
                elif datatype == 'date':
                    xml += '   <%s>%s</%s>\n' % (n,tu.d(v).strftime('%a %d %b').decode('utf8'),n)
                elif datatype == 'datetime':
                    xml += '   <%s>%s</%s>\n' % (n,tu.dt(v).strftime('%x %X'),n)
                elif n == 'attendance_ids' and isinstance(v, list) and len(v)>0:
                    xml += ' <attendances>\n'
                    for att in pool_att.browse(cr, uid, v):
                        xml += '  <attendance>\n'
                        xml += '   <time>%s</time>\n' % \
                            tu.dt(att.name).strftime('%H:%M')
                        xml += '   <action>%s</action>\n' % att.action
                        xml += '   <reason>%s</reason>\n' % (att.action_desc and
                                                           att.action_desc.name
                                                           or '')
                        xml += '  </attendance>\n'
                    xml += ' </attendances>\n'
                elif n == 'holiday_ids' and isinstance(v, list) and len(v)>0:
                    xml += ' <holidays>\n'
                    hols = pool_hol.browse(cr, uid, v)
                    legal_hols = [ h for h in hols if h.holiday_status.section_id and h.holiday_status.section_id.name == 'Licencia' ]
                    xml += ' <legals>\n'
                    for hol in legal_hols:
                        xml += '  <holiday>\n'
                        xml += '   <name>%s</name>\n' % hol.name
                        xml += '   <state>%s</state>\n' % hol.name
                        xml += '   <status>%s</status>\n' % (hol.holiday_status and
                                                             hol.holiday_status.name or
                                                             '')
                        xml += '   <date-from>%s</date-from>\n' % tu.dt(hol.date_from).strftime('%d/%m %H:%M')
                        #xml += '   <date-from>[[ formatLang('%s', date=True)]]</date-from>\n' % tu.dt(hol.date_from).strftime('%d/%m %H:%M')
                        xml += '   <date-to>%s</date-to>\n' % tu.dt(hol.date_to).strftime('%d/%m %H:%M')
                        xml += '   <notes>%s</notes>\n' % hol.notes
                        xml += '  </holiday>\n'
                    xml += ' </legals>\n'
                    nolegal_hols = [ h for h in hols if h not in legal_hols ]
                    xml += ' <out>\n'
                    for hol in nolegal_hols:
                        xml += '  <holiday>\n'
                        xml += '   <name>%s</name>\n' % hol.name
                        xml += '   <state>%s</state>\n' % hol.name
                        xml += '   <status>%s</status>\n' % (hol.holiday_status and
                                                             hol.holiday_status.name or
                                                             '')
                        xml += '   <date-from>%s</date-from>\n' % tu.dt(hol.date_from).strftime('%d/%m %H:%M')
                        #xml += '   <date-from>[[ formatLang('%s', date=True)]]</date-from>\n' % tu.dt(hol.date_from).strftime('%d/%m %H:%M')
                        xml += '   <date-to>%s</date-to>\n' % tu.dt(hol.date_to).strftime('%d/%m %H:%M')
                        xml += '   <notes>%s</notes>\n' % hol.notes
                        xml += '  </holiday>\n'
                    xml += ' </out>\n'

                    xml += ' </holidays>\n'
                elif isinstance(v, list):
                    continue
                else:
                    xml += '   <%s>%s</%s>\n' % (n,v,n)
            xml += '  </journal>\n'
        xml += ' <sums>\n'
        for k,v in sums.items():
            xml += '  <%s>%7.2f</%s>\n' % (k,v,k)
        xml += ' </sums>\n'

        xml += '</journals>\n'
        return xml

    def get_journals(self, cr, uid, emp_id, context):
        pool_journal = self.pool.get('hr.aa.journal')
        journal_ids = pool_journal.search(cr, uid, [
            ('employee_id', '=', emp_id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ], context=context)
        return journal_ids

    def create_xml(self, cr, uid, ids, data, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        self.date_from = data['form']['date_from']
        self.date_to = data['form']['date_to']
        self.xml_fields = False
        pool_employee = self.pool.get('hr.employee')
        pool_journal = self.pool.get('hr.aa.journal')

        xml = u'<?xml version="1.0" encoding="UTF-8" ?>\n'

        xml += '<report>\n%s\n'
        xml += '<date>%s</date>\n' % tu.datetime.now().strftime(
            '%A, %d %B %Y, %H:%M').decode('utf8')
        for employee_id in ids:
            xml += '<entry>\n'
            xml += self.gen_xml_employee(cr, uid, [employee_id], context)
            journal_ids = self.get_journals(cr, uid, employee_id, context)
            xml += self.gen_xml_journals(cr, uid, journal_ids, context)
            xml += '</entry>\n'

        xml %= self.xml_fields
        xml += '</report>\n'

        import codecs
        f = codecs.open('/tmp/test.journal.xml', 'w', encoding='utf8')
        f.write(xml)
        f.close()


        return xml

report_custom('report.hr.aa.print_journal_report',
              'hr.employee',
              '',
              'addons/hr_attendance_analysis/report/journal_report.xsl')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
