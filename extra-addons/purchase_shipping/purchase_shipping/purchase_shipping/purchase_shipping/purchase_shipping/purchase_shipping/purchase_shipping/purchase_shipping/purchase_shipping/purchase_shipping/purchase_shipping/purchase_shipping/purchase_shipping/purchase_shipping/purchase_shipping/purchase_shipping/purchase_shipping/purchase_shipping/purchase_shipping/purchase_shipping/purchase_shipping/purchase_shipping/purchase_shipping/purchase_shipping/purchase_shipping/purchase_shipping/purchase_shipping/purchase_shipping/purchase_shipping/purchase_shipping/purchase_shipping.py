# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import fields, osv

class purchase_shipping(osv.osv):
    _name = "purchase.shipping"
    _columns = {
        'shipment_qty':fields.char('Quantite',size=64),
        'boat':fields.char('Bateau', size=64), 
        'estimated_departure':fields.date('ETD'),
        'embarcation_port':fields.char('Port Embarcation', size=64),
        'estimated_arival':fields.date('ETA'),
        'bsc_number':fields.char('N° BSC', size=64),
        'carrier':fields.char('Transitaire', size=64),
        'carrier_document':fields.char('Document Transitaire', size=64),
        'container_number':fields.char('N° Containeur', size=64),
        'stage_date':fields.date('Date de situation'),
        'stage':fields.char('Etat', size=64),
        'destination':fields.char('Motif', size=64),
        'original_document':fields.boolean('Doc. Originale'),
        'copy_document':fields.boolean('Doc. Copie'),
        'dom':fields.char('Dom', size=64),
        'lc_number':fields.char('N° LC', size=64),
        'order_id':fields.many2one('purchase.order', 'Order'),
        'name':fields.char('Nom', size=64),
    }


    def onchange_stage(self, cr, uid, ids, stage):
        return {'value':{'stage_date': (time.strftime('%Y-%m-%d'))}}


    _defaults = {'stage_date':lambda *a: time.strftime('%Y-%m-%d'),}
    
purchase_shipping()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'shipment_ids':fields.one2many('purchase.shipping', 'order_id', 'Shipments'),
        'origin':fields.char('Origine', size=64),
        'partner_state':fields.selection((('wait_offer','Attente Offre'),('wait_ar','Attente AR'),('groupage','Groupage'),('container','Conteneur Complet')),'Etat'),
        'file_number':fields.char('Numero Dossier', size=64),
        'embarcation_expected':fields.char('Emarquement', size=64),
        'embarcation_date':fields.date('Date Emarquement')
    }
purchase_order()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'local_supplier':fields.boolean('Fournisseur Local'),
        'foreign_supplier':fields.boolean('Fournisseur Import'),
        'group_supplier':fields.boolean('Fournisseur Group'),
    }
res_partner()

