# -*- encoding: utf-8 -*-
##############################################################################
#
#    Attendance Annalysis for OpenERP
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

{
	"name" : "Human Resources Attendance Annalysis",
	"version" : "1.1",
	"author" : "Moldeo Interactive CT",
    "category" : "Localisation/America", # TODO: Cambiar al adecuado.

    "website" : "http://www.moldeointeractive.com.ar",
    "description": """
    Module to do analisis over human resources attendances.
    """,
	"init_xml" : [],
	"update_xml" : [
        "hr_attendance_analysis_workflow.xml",
        "hr_attendance_analysis_view.xml",
        "hr_attendance_analysis_wizard.xml",
        "hr_action_reason_rule_view.xml",
        "hr_action_reason_rule_wizard.xml",
        "hr_action_reason_rule_workflow.xml",
        "hr_journal_view.xml",
        "hr_journal_wizard.xml",
        "hr_journal_workflow.xml",
        "hr_payroll_view.xml",
        "hr_payroll_report.xml",
        "hr_payroll_workflow.xml",
        "hr_payroll_wizard.xml",
    ],
	"installable": True,
	"active": False,
}
