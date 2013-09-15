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
	'period_id':fields.many2one('account.period','Periode'),
        'cot_base':fields.float('Base Cotisations'),
        'cnaps_employee':fields.float('CNaPS Salarie'),
        'cnaps_employer':fields.float('CNAPS Employeur'),
        'medicale_employee':fields.float('Medicale Salarie'),
        'medicale_employer':fields.float('Medicale Employeur'),
        'irsa_base':fields.float('Base IRSA'),
        'irsa':fields.float('IRSA'),
        'total_employer':fields.float('Total Cot. Patronale'),
        'total_employee_cost':fields.float('Total Cout Salarie'),
	}
    _order = 'matricule desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_salary_report')
        cr.execute("""
CREATE OR REPLACE VIEW hr_salary_report AS 
 SELECT min(hr_payroll_ma_bulletin_line.id_bulletin) AS id, hr_employee.matricule, hr_employee.id AS employee_id, hr_payroll_ma_bulletin.salaire_brute, hr_payroll_ma_bulletin.period_id, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = 'CNaPS'::text THEN hr_payroll_ma_bulletin_line.base
            ELSE 0::numeric
        END) AS cot_base, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = 'CNaPS'::text THEN hr_payroll_ma_bulletin_line.subtotal_employee
            ELSE 0::numeric
        END) AS cnaps_employee, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = 'CNaPS'::text THEN hr_payroll_ma_bulletin_line.subtotal_employer
            ELSE 0::numeric
        END) AS cnaps_employer, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = ANY (ARRAY['OSTIE'::character varying, 'FUNHECE'::character varying, 'SMIA'::character varying]::text[]) THEN hr_payroll_ma_bulletin_line.subtotal_employee
            ELSE 0::numeric
        END) AS medicale_employee, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = ANY (ARRAY['OSTIE'::character varying, 'FUNHECE'::character varying, 'SMIA'::character varying]::text[]) THEN hr_payroll_ma_bulletin_line.subtotal_employer
            ELSE 0::numeric
        END) AS medicale_employer, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = 'Impot sur le revenu'::text THEN hr_payroll_ma_bulletin_line.base
            ELSE 0::numeric
        END) AS irsa_base, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = 'Impot sur le revenu'::text THEN hr_payroll_ma_bulletin_line.subtotal_employee
            ELSE 0::numeric
        END) AS irsa, sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = ANY (ARRAY['OSTIE'::character varying, 'FUNHECE'::character varying, 'SMIA'::character varying, 'CNaPS'::character varying, 'Impot sur le revenu'::character varying]::text[]) THEN hr_payroll_ma_bulletin_line.subtotal_employer
            ELSE 0::numeric
        END) AS total_employer,
        sum(
        CASE
            WHEN hr_payroll_ma_bulletin_line.name::text = ANY (ARRAY['OSTIE'::character varying, 'FUNHECE'::character varying, 'SMIA'::character varying, 'CNaPS'::character varying, 'Impot sur le revenu'::character varying]::text[]) THEN hr_payroll_ma_bulletin_line.subtotal_employer
            ELSE 0::numeric
        END)+hr_payroll_ma_bulletin.salaire_brute AS total_employee_cost

        
   FROM hr_payroll_ma_bulletin, hr_payroll_ma_bulletin_line, hr_employee, resource_resource
  WHERE hr_payroll_ma_bulletin.employee_id = hr_employee.id AND hr_payroll_ma_bulletin_line.id_bulletin = hr_payroll_ma_bulletin.id AND hr_employee.resource_id = resource_resource.id
  GROUP BY hr_payroll_ma_bulletin.period_id, hr_payroll_ma_bulletin_line.id_bulletin, hr_employee.matricule, hr_employee.id, hr_payroll_ma_bulletin.salaire_brute;

ALTER TABLE hr_salary_report
  OWNER TO openerp;
        """)

hr_salary_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
