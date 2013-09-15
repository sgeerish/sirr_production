#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import time

import netsvc
from osv import fields, osv
import tools
from tools.translate import _
import decimal_precision as dp

class hr_employee(osv.osv):
    '''
    Employee
    '''

    _inherit = 'hr.employee'
    _description = 'Employee'

    _columns = {
                'pan':fields.char('PAN No',size=32),
                'esi':fields.char('ESI No',size=32),
                'pf' :fields.char('PF No', size=32),
    }

hr_employee()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
