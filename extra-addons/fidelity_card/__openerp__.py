##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
{
    "name" : "Gestion de carte de fidelite",
    "author" : "OpenMind Ltd",
    "version" : "1.0",
    "description" : """The document_lock adds a status on the attachment, allowing you to lock attachments or not.""",    
    "category" : "Generic Modules/Sales & Purchases",
    "depends" : ["base", "account"],
    "demo_xml" : [],
    "update_xml" : ["card_sequence.xml","card_view.xml","security/sale_security.xml","security/ir.model.access.csv"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
