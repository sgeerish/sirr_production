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

from osv import osv, fields

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_pickings(self, cr, uid, ids, context=None):
        res = set()
        for move in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            if move.picking_id:
                res.add(move.picking_id.id)
        return list(res)

    _columns = {
        'location_id':fields.related('move_lines', 'location_id', type='many2one',
            relation='stock.location', string='Source Location', select=2,
            store={
                'stock.move': (_get_pickings, ['location_id', 'location_dest_id'], 20)
            }),
        'location_dest_id':fields.related('move_lines', 'location_dest_id',
            type='many2one', relation='stock.location', string='Dest. Location', select=2,
            store={
                'stock.move': (_get_pickings, ['location_id', 'location_dest_id'], 20)
            }),
    }

stock_picking()

class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'

    def _get_locations(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids):
            location_ids = set()
            for move in inv.inventory_line_id:
                location_ids.add(move.location_id.id)
            res[inv.id] = list(location_ids)
        return res

    def _location_ids_search(self, cr, uid, obj, name, args, context=None):
        for arg in args:
            if arg[0] == 'location_ids':
                operator = arg[1]
                search_term = arg[2]
        if operator and search_term:
            move_obj = self.pool.get('stock.inventory.line')
            move_ids = move_obj.search(cr, uid,
                [('location_id', operator, search_term)], context=context)
        else:
            move_ids = []
        return [('inventory_line_id', 'in', move_ids)]

    _columns = {
        'location_ids':fields.function(_get_locations, fnct_search=_location_ids_search,
            method=True, type='many2many', relation='stock.location', string='Related Locations'),
    }

stock_inventory()