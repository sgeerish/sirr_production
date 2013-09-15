# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import tools
from osv import fields, osv
class hr_salary_report(osv.osv):
    _name = "hr.salary.report"
    _description = "Rapport de salaire"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'matricule': fields.char('Matricule', size=32, readonly=True),
	'employee_id':fields.many2one('hr.employee','Nom'),
	'salaire_brute':fields.float('Salaire Brut'),
	'period_id':fields.many2one('account.period'),
        'cot_base':fields.float('Base Cotisations'),
        'cnaps_employee':fields.float('CNaPS Salarie'),
        'cnaps_employer':fields.float('CNAPS Employeur'),
        'medicale_employee':fields.float('Medicale Salarie'),
        'medicale_employer':fields.float('MEdicale Employeur'),
        'irsa_base':fields.float('Base IRSA'),
        'irsa':fields.float('IRSA'),
        'total_employer':fields.float('Total Cot. Patronale'),
	}
    _order = 'matricule desc'

hr_salary_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
