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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

{
	"name" : "Clock Reader",
	"version" : "1.0",
	"author" : "Moldeo Interactive CT",
    "category" : "Localisation/America", # TODO: Cambiar al adecuado.
	"depends" : ["hr_attendance"],
    "website" : "http://www.moldeointeractive.com.ar",
    "description": """
    Module to load personal assistance from Employee Time Clocks.

    It' support F-5 clocks.
    """,
	"init_xml" : [],
	"update_xml" : [
        "security/clock_reader_security.xml",
        "security/ir.model.access.csv",
        "clock_reader_view.xml",
        "clock_reader_wizard.xml",
    ],
	"demo_xml" : [],
	"installable": True,
	"active": False,
}
