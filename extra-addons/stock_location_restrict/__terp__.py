# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Gábor Dukai <gdukai@gmail.com>
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
    "name" : "Restrict access to moves, pickings and locations",
    "version" : "0.1",
    "author" : "Gábor Dukai",
    "website" : "http://exploringopenerp.blogspot.com",
    "license" : "GPL-3",
    "description": """
    This module allows filtering of pickings and stock inventories
    by location. It's useful to restrict stock workers to only see
    those pickings that are relevant to them.

    Technically: pickings get their unused location_id, location_dest_id
    fields redefined to be filled in from their moves' data.
    Inventories get a location_ids field from their lines' data.
    Record rules can be set on these fields like this for stock.picking:
    ['|', ('move_lines','=',[]),'|',('location_id','in',[11]),
    ('location_dest_id','in',[11])]
    will restrict the user to only see pickings that has moves
    from or to the location with ID 11.
    This will restrict stock.move (works without this module):
    ['|',('location_id','in',[11]),('location_dest_id','in',[11])]
    This will restrict stock.inventory:
    ['|',('inventory_line_id','=',[]),('location_ids','in',[11])]

    Compatibility: tested with OpenERP v5.0
    """,
    "depends" : ["stock", ],
    "init_xml" : [],
    "update_xml" : [
                   ],
    "installable" : True,
    "active" : False,
}
