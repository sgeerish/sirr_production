##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    
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
{
    "name" : "Sale order stock control",
    "version" : "0.1",
    "depends" : ["base","sale"],
    "author" : "Vox Teneo",
    "description" : """
    This module adds a step in the sale order workflow to control that each order
    line have enough virtual stock.
    """,
    "website" : "http://www.voxteneo.com",
    "category" : "Added functionality",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
    	"sale_order_line_view.xml",
    ],
    "active": False,
    "installable": True,
}				
