# -*- coding: utf-8 -*-
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

from tools.translate import _
from osv import fields, osv

class medical_installer_modules(osv.osv_memory):
    _name = 'medical.installer.modules'
    _inherit = 'res.config.installer'
    _columns = {
        # Medical

        'medical_socioeconomics':fields.boolean('Medical Socioeconomics',
            help="Allow to enter social economic details of Patient."),
        'medical_lifestyle':fields.boolean('Medical Lifestyle',
            help="Allow to enter Patient's lifestyle details."),
        'medical_genetics':fields.boolean('Medical Genetics',
            help="This module allows Family history and genetic risks"
                "The module includes hereditary risks, family history and genetic disorders."
                "In this module we include the NCBI and Genecard information, more than 4200 genes associated to diseases"),
        'medical_icd10':fields.boolean('Medical ICD-10',
            help="This module will install WHO International Classification of Diseases 10th Revision."),
        'medical_lab': fields.boolean('Medical Lab',
            help="Medical Lab module used for Lab Management and lab test reports and invoicing."),
        'medical_surgery': fields.boolean('Medical Surgery',
            help="Medical Surgery module used for patient's surgery details."),
        'medical_icd10pcs': fields.boolean('Medical ICD-10-PCS',
            help="Medical International Classification of Diseases 10th Revision - Procedure Coding System, used to code the surgical and therapeutic procedures"),
         'medical_gyneco': fields.boolean('Medical Gyneco / Obstetrics',
            help="""This module includes :\n
                - Gynecological Information\n
                - Obstetric information\n 
                - Perinatal Information and monitoring\n
                - Puerperium. """),
        'medical_inpatient': fields.boolean('Medical Inpatient',
            help="""This module will hold all the processes related to Inpatient (Patient hospitalization)\n
                - Patient Registration\n
                - Bed reservation\n
                - Hospitalization\n
                - Nursing Plan\n
                - Discharge Plan\n
                - Reporting"""),
        'medical_invoice': fields.boolean('Medical Invoicing',
            help="This module add functionality to create invoices for doctor's consulting charge."),
    }

    _defaults = {
        'medical_socioeconomics': True,
        'medical_lifestyle': True,
        'medical_lab': True,
        'medical_icd10': True,
        'medical_genetics': True,
        'medical_gyneco': True,
        'medical_inpatient': True,
        'medical_surgery': True,
        'medical_invoice': True,

    }

medical_installer_modules()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
