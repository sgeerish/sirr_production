# coding=utf-8

#    Copyright (C) 2008-2010  Luis Falcon

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time
from mx import DateTime
import datetime
from osv import fields, osv
from tools.translate import _

#DEBUG MODE -- DELETE ME !
# import pdb


class insurance (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['number','company'], context)
		res = []
		for record in reads:
			name = record['number']
			if record['company']:
				name = record['company'][1] + ': ' +name
			res.append((record['id'], name))
		return res


	_name = "medical.insurance"
	_columns = {
		'name' : fields.many2one ('res.partner','Owner'), 
		'number' : fields.char ('Number', size=64),
		'company' : fields.many2one ('res.partner','Insurance Company'),
		'member_since' : fields.date ('Member since'),
		'member_exp' : fields.date ('Expiration date'),
		'category' : fields.char ('Category', size=64, help="Insurance company plan / category"),
		'type' : fields.selection([
                                ('state','State'),
                                ('labour_union','Labour Union / Syndical'),
                                ('private','Private'),

                                ], 'Insurance Type', select=True),

		'notes' : fields.text ('Extra Info'),

		}
insurance ()



class partner_patient (osv.osv):
	_name = "res.partner"
	_inherit = "res.partner"
	_columns = {
		'date' : fields.date('Partner since',help="Date of activation of the partner or patient"),
		'alias' : fields.char('alias', size=64),
		'ref': fields.char('ID Number', size=64),
                'is_person' : fields.boolean('Person', help="Check if the partner is a person."),
                'is_patient' : fields.boolean('Patient', help="Check if the partner is a patient"),
                'is_doctor' : fields.boolean('Doctor', help="Check if the partner is a doctor"),
		'is_institution' : fields.boolean ('Institution', help="Check if the partner is a Medical Center"),
		'lastname' : fields.char('Last Name', size=128, help="Last Name"),
		'insurance' : fields.one2many ('medical.insurance','name',"Insurance"),	
		'user_id': fields.many2one('res.users', 'Internal User', help='In Medical is the user (doctor, nurse) that logins into OpenERP that will relate to the patient or family. When the partner is a doctor or a health proffesional, it will be the user that maps the doctor\'s partner name. It must be present.'),

	}
        _sql_constraints = [
                ('ref_uniq', 'unique (ref)', 'The partner or patient code must be unique')
 		]

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['name', 'lastname'], context)
		res = []
		for record in reads:
			name = record['name']
			if record['lastname']:
				name = record['lastname'] + ', '+name
			res.append((record['id'], name))
		return res


partner_patient ()


class product_medical (osv.osv):
	_name = "product.product"
	_inherit = "product.product"
	_columns = {
                'is_medicament' : fields.boolean('Medicament', help="Check if the product is a medicament"),
                'is_vaccine' : fields.boolean('Vaccine', help="Check if the product is a vaccine"),
                'is_bed' : fields.boolean('Bed', help="Check if the product is a bed on the medical center"),

	}
product_medical ()


#Add the partner relationship field to the contacts.
class partner_patient_address (osv.osv):
	_name = "res.partner.address"
	_inherit = "res.partner.address"
	_columns = {
		'relationship' : fields.char('Relationship', size=64, help="Include the relationship with the patient - friend, co-worker, brother, ...- "),
		'relative_id' : fields.many2one('res.partner','Relative Partner ID', domain=[('is_patient', '=', True)], help="If the relative is also a patient, please include it here"),
	}
partner_patient_address ()


class procedure_code (osv.osv):
	_description = "Medical Procedure"
	_name = "medical.procedure"
	_columns = {
		'name': fields.char ('Code', size=16, required=True),
		'description' : fields.char ('Long Text', size=256),
		}

	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
        	args2 = args[:]
        	if name:
            		args += [('name', operator, name)]
            		args2 += [('description', operator, name)]
        	ids = self.search(cr, uid, args, limit=limit)
        	ids += self.search(cr, uid, args2, limit=limit)
        	res = self.name_get(cr, uid, ids, context)
        	return res

procedure_code ()



class pathology_category(osv.osv):
        def name_get(self, cr, uid, ids, context={}):
                if not len(ids):
                        return []
                reads = self.read(cr, uid, ids, ['name','parent_id'], context)
                res = []
                for record in reads:
                        name = record['name']
                        if record['parent_id']:
                                name = record['parent_id'][1]+' / '+name
                        res.append((record['id'], name))
                return res

        def _name_get_fnc(self, cr, uid, ids, prop, foo, faa):
                res = self.name_get(cr, uid, ids)
                return dict(res)
        def _check_recursion(self, cr, uid, ids):
                level = 100
                while len(ids):
                        cr.execute('select distinct parent_id from medical_pathology_category where id in ('+','.join(map(str,ids))+')')
                        ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                        if not level:
                                return False
                        level -= 1
                return True

        _description='Disease Categories'
        _name = 'medical.pathology.category'
        _columns = {
                'name': fields.char('Category Name', required=True, size=128),
                'parent_id': fields.many2one('medical.pathology.category', 'Parent Category', select=True),
                'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
                'child_ids': fields.one2many('medical.pathology.category', 'parent_id', 'Children Category'),
                'active' : fields.boolean('Active'),
        }
        _constraints = [
                (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
        ]
        _defaults = {
                'active' : lambda *a: 1,
        }
        _order = 'parent_id,id'

pathology_category()


class pathology (osv.osv):
	_name = "medical.pathology"
	_description = "Diseases"
	_columns = {
		'name' : fields.char ('Name', size=128, help="Disease name"),
		'code' : fields.char ('Code', size=32, help="Specific Code for the Disease (eg, ICD-10, SNOMED...)"),
		'category' : fields.many2one('medical.pathology.category','Disease Category'),
		'chromosome' : fields.char ('Affected Chromosome', size=128, help="chromosome number"),
		'protein' : fields.char ('Protein involved', size=128, help="Name of the protein(s) affected"),
		'gene' : fields.char ('Gene', size=128, help="Name of the gene(s) affected"),
		'info' : fields.text ('Extra Info'),
	}

        _sql_constraints = [
                ('code_uniq', 'unique (code)', 'The disease code must be unique')]


	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
        	args2 = args[:]
        	if name:
            		args += [('name', operator, name)]
            		args2 += [('code', operator, name)]
        	ids = self.search(cr, uid, args, limit=limit)
        	ids += self.search(cr, uid, args2, limit=limit)
        	res = self.name_get(cr, uid, ids, context)
        	return res

pathology ()


class medicament (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

	_name = "medical.medicament"
	_columns = {
		'name' : fields.many2one ('product.product','Name', domain=[('is_medicament', '=', "1")],help="Commercial Name"),
		'active_component' : fields.char ('Active component', size=128, help="Active Component"),
		'therapeutic_action' : fields.char ('Therapeutic effect', size=128, help="Therapeutic action"),
		'composition' : fields.text ('Composition',help="Components"),
		'indications' : fields.text ('Indication',help="Indications"),
		'dosage' : fields.text ('Dosage Instructions',help="Dosage / Indications"),
		'overdosage' : fields.text ('Overdosage',help="Overdosage"),
		'pregnancy_warning' : fields.boolean ('Pregnancy Warning', help="Check when the drug can not be taken during pregnancy or lactancy"),
		'pregnancy' : fields.text ('Pregnancy and Lactancy',help="Warnings for Pregnant Women"),
		'presentation' : fields.text ('Presentation',help="Packaging"),
		'adverse_reaction' : fields.text ('Adverse Reactions'),
		'storage' : fields.text ('Storage Conditions'),
		'price' : fields.related ('name','lst_price',type='float',string='Price'),
		'qty_available' : fields.related ('name','qty_available',type='float',string='Quantity Available'),
		'notes' : fields.text ('Extra Info'),
		}

medicament ()




class operational_area (osv.osv):
	_name = "medical.operational_area"
	_columns = {
		'name' :fields.char ('Name', size=128, help="Operational Area of the city or region"),
		'info' :fields.text ('Extra Information'),
		}

        _sql_constraints = [
                ('code_uniq', 'unique (name)', 'The Operational Area code name must be unique')]

operational_area ()

class operational_sector (osv.osv):
	_name = "medical.operational_sector"
	_columns = {
		'name' :fields.char ('Name', size=128, help="Region included in an operational area"),
		'operational_area' :fields.many2one ('medical.operational_area','Operational Area'),
		'info' :fields.text ('Extra Information'),
		}

        _sql_constraints = [
                ('code_uniq', 'unique (name,operational_area)', 'The Operational Sector code and OP Area combination must be unique')]

operational_sector ()

class family_code (osv.osv):
	_name = "medical.family_code"
	_columns = {
		'name' :fields.char ('Name', size=128, help="Family code within an operational sector"),
		'operational_sector' :fields.many2one ('medical.operational_sector','Operational Sector'),
		'members_ids' : fields.many2many ('res.partner', 'family_members_rel','family_id','members_id', 'Members',domain=[('is_person', '=', "1")]),
		'info' :fields.text ('Extra Information'),
		}

        _sql_constraints = [
                ('code_uniq', 'unique (name)', 'The Family code name must be unique')]

family_code ()

class speciality (osv.osv):
	_name = "medical.speciality"
	_columns = {
		'name' :fields.char ('Description', size=128, help="ie, Addiction Psychiatry"),
		'code' : fields.char ('Code', size=128, help="ie, ADP"),
	}
        _sql_constraints = [
                ('code_uniq', 'unique (name)', 'The Medical Speciality code must be unique')]

speciality ()


class physician (osv.osv):


	_name = "medical.physician"
	_description = "Information about the doctor"
	_columns = {
		'name' : fields.many2one ('res.partner','Physician', domain=[('is_doctor', '=', "1")], help="Physician's Name, from the partner list"),
		'institution' : fields.many2one ('res.partner','Institution',domain=[('is_institution', '=', "1")],help="Instituion where she/he works"),
		'code' : fields.char ('ID', size=128, help="MD License ID"),
		'speciality' : fields.many2one ('medical.speciality','Speciality', help="Speciality Code"),
		'info' : fields.text ('Extra info'),
		}

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

physician ()





class ethnic_group (osv.osv):
	_name ="medical.ethnicity"
	_columns = {
		'name' : fields.char ('Ethnic group',size=128),
		'code' : fields.char ('Code',size=64),
		}

ethnic_group ()

class occupation (osv.osv):
	_name = "medical.occupation"
	_description = "Occupation / Job"
	_columns = {
		'name' : fields.char ('Occupation', size=128),
		'code' : fields.char ('Code', size=64),
		}
occupation ()

class medical_dose (osv.osv):
	_name = "medical.dose.unit"
	_columns = {
		'name' : fields.char ('Unit',size=32),
		'desc' : fields.char ('Description',size=64),
		}

medical_dose ()


class medical_drug_route (osv.osv):
	_name = "medical.drug.route"
	_columns = {
		'name' : fields.char ('Route',size=64, translate=True),
		'code' : fields.char ('Code',size=32),
		}
medical_drug_route ()


class medical_drug_form (osv.osv):
	_name = "medical.drug.form"
	_columns = {
		'name' : fields.char ('Form',size=64, translate=True),
		'code' : fields.char ('Code',size=32),
		}
medical_drug_form ()


# PATIENT GENERAL INFORMATION 
	
class patient_data (osv.osv):

	def name_get(self, cr, user, ids, context={}):
		if not len(ids):
			return []
		def _name_get(d):
			name = d.get('name','')
			id = d.get('patient_id',False)
			if id:
				name = '[%s] %s' % (id,name[1])
			return (d['id'], name)
		result = map(_name_get, self.read(cr, user, ids, ['name','patient_id'], context))
		return result

	def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
		if not args:
			args=[]
		if not context:
			context={}
		if name:
			ids = self.search(cr, user, [('patient_id','=',name)]+ args, limit=limit, context=context)
			if not len(ids):
				ids += self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
		else:
			ids = self.search(cr, user, args, limit=limit, context=context)
		result = self.name_get(cr, user, ids, context)
		return result    


# Automatically assign the family code

	def onchange_partnerid (self, cr, uid, ids, partner):
		family_code_id = ""
		if partner:
 			cr.execute ('select family_id from family_members_rel where members_id=%s limit 1',(partner,))
			try:
				family_code_id = str(cr.fetchone()[0])
			except:
				family_code_id = ""
			
		v = {'family_code':family_code_id}
		
		return {'value': v}	

	
# Get the patient age in the following format : "YEARS MONTHS DAYS"
# It will calculate the age of the patient while the patient is alive. When the patient dies, it will show the age at time of death.
		
	def _patient_age(self, cr, uid, ids, name, arg, context={}):
		def compute_age_from_dates (patient_dob,patient_deceased,patient_dod):
			now=DateTime.now()
			if (patient_dob):
				dob=DateTime.strptime(patient_dob,'%Y-%m-%d')
				if patient_deceased :
					dod=DateTime.strptime(patient_dod,'%Y-%m-%d %H:%M:%S')
					delta=DateTime.Age (dod, dob)
					deceased=" (deceased)"
				else:
					delta=DateTime.Age (now, dob)
					deceased=''
				years_months_days = str(delta.years) +"y "+ str(delta.months) +"m "+ str(delta.days)+"d" + deceased
			else:
				years_months_days = "No DoB !"
			
 
			return years_months_days
		result={}
	        for patient_data in self.browse(cr, uid, ids, context=context):
	            result[patient_data.id] = compute_age_from_dates (patient_data.dob,patient_data.deceased,patient_data.dod)
	        return result

	_name = "medical.patient"
	_description = "Patient related information"
	_columns = {
                'name' : fields.many2one('res.partner','Patient', required="1", domain=[('is_patient', '=', True),('is_person', '=', True) ], help="Patient Name"),
                'patient_id': fields.char('ID', size=64, required=True, select=True, help="Patient Identifier provided by the Health Center. Is not the patient id from the partner form"),	
		'lastname' : fields.related ('name','lastname',type='char',string='Lastname'), 
		'family_code' : fields.many2one ('medical.family_code','Family',help="Family Code"),
		'identifier' : fields.related ('name','ref',type='char',string='SSN', help="Social Security Number or National ID"),
		'current_insurance': fields.many2one ('medical.insurance',"Insurance", domain="[('name','=',name)]",help="Insurance information. You may choose from the different insurances belonging to the patient"),
		'current_address': fields.many2one ('res.partner.address', "Address", domain="[('partner_id','=',name)]", help="Contact information. You may choose from the different contacts and addresses this patient has"),
		'primary_care_doctor': fields.many2one('medical.physician','Primary Care Doctor', help="Current primary care / family doctor"),

		'photo' : fields.binary ('Picture'),
		'dob' : fields.date ('Date of Birth'),
		'age' : fields.function(_patient_age, method=True, type='char', size=32, string='Patient Age',help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
		'sex' : fields.selection([
                                ('m','Male'),
                                ('f','Female'),
                                ], 'Sex', select=True),
		'marital_status' : fields.selection([
                                ('s','Single'),
                                ('m','Married'),
				('w','Widowed'),
				('d','Divorced'),
				('x','Separated'),
                                ], 'Marital Status'),
		'blood_type' : fields.selection([
				('A','A'),
				('B','B'),
				('AB','AB'),
				('O','O'),
				], 'Blood Type'),
		'rh' : fields.selection([
				('+','+'),
				('-','-'),
				], 'Rh'),


		'user_id':fields.related('name','user_id',type='many2one',relation='res.partner',string='Doctor',help="Physician that logs in the local Medical system (HIS), on the health center. It doesn't necesarily has do be the same as the Primary Care doctor"),
		'ethnic_group' : fields.many2one ('medical.ethnicity','Ethnic group'),
		'vaccinations': fields.one2many ('medical.vaccination','name',"Vaccinations"),
		'medications' : fields.one2many('medical.patient.medication','name','Medications'),
		'prescriptions': fields.one2many ('medical.prescription.order','name',"Prescriptions"),
		'diseases' : fields.one2many ('medical.patient.disease', 'name', 'Diseases'),
		'critical_info' : fields.text ('Important disease, allergy or procedures information',help="Write any important information on the patient's disease, surgeries, allergies, ..."),
		'evaluation_ids' : fields.one2many ('medical.patient.evaluation','name','Evaluation'),
		'admissions_ids' : fields.one2many ('medical.patient.admission','name','Admission / Discharge'),
		'general_info' : fields.text ('General Information',help="General information about the patient"),
		'deceased' : fields.boolean ('Deceased',help="Mark if the patient has died"),
		'dod' : fields.datetime ('Date of Death'),
		'cod' : fields.many2one ('medical.pathology', 'Cause of Death'),

	}

	_defaults={
		'patient_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'medical.patient'),
		}
		
        _sql_constraints = [
                ('name_uniq', 'unique (name)', 'The Patient already exists')]

patient_data ()

class appointment (osv.osv):
	_name = "medical.appointment"

#Additions from Nhomar Hernandez (nhomar)

	def copy(self, cr, uid, id, default=None, context=None):
		if not default:
			default = {}
		default.update({
			'name': self.pool.get('ir.sequence').get(cr, uid, 'medical.appointment'),
		})
		return super(appointment, self).copy(cr, uid, id, default, context=context)

#End of additions from nhomar

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		res = []
		for r in self.read(cr, uid, ids, ['rec_name','appointment_date'],context):
			date = str(r['appointment_date'] or '')
			res.append((r['id'], date))
		return res


	_columns = {
        
		'doctor' : fields.many2one ('res.partner','Physician', domain=[('is_doctor', '=', "1")], help="Physician's Name"),
		'name' : fields.char ('Appointment ID',size=64, readonly=True, required=True),
		'patient' : fields.many2one ('medical.patient','Patient', help="Patient Name"),
		'appointment_date' : fields.datetime ('Date and Time'),
		'institution' : fields.many2one ('res.partner','Health Center', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'speciality' : fields.many2one ('medical.speciality','Speciality', help="Medical Speciality / Sector"),
		'urgency' : fields.selection([
				('a','Normal'),
				('b','Urgent'),
				('c','Medical Emergency'),
				], 'Urgency Level'),

		'comments' : fields.text ('Comments'),

#Additions from Husen Daudi (hda)
		'user_id':fields.related('doctor','user_id',type='many2one',relation='res.partner',string='Physician'),

#End of additions from hda

		'patient_status': fields.selection([
				('ambulatory','Ambulatory'),
				('outpatient','Outpatient'),
				('inpatient','Inpatient'),
				], 'Patient status'),


		}
	_order = "appointment_date desc"

	_defaults = {
           'urgency': lambda *a: 'a',
	        'name': lambda self, cr, uid, context=None: \
		self.pool.get('ir.sequence').get(cr, uid, 'medical.appointment'),
		'appointment_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'patient_status': lambda *a: 'ambulatory',
        	}
	

appointment ()


# PATIENT DISESASES INFORMATION

class patient_disease_info (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'pathology'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

	_name = "medical.patient.disease"
	_description = "Disease info"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID',readonly=True),
		'pathology' : fields.many2one ('medical.pathology','Disease',required=True, help="Disease"),
		'disease_severity' : fields.selection ([
			('1_mi','Mild'),
			('2_mo','Moderate'),
			('3_sv','Severe'),
			], 'Severity', select=True),		
		'is_on_treatment' : fields.boolean ('Currently on Treatment'),
		'is_infectious' : fields.boolean ('Infectious Disease',help="Check if the patient has an infectious / transmissible disease"),		
		'short_comment' : fields.char ('Remarks', size=128,help="Brief, one-line remark of the disease. Longer description will go on the Extra info field"),
		'doctor' : fields.many2one('medical.physician','Physician', help="Physician who treated or diagnosed the patient"),
		'diagnosed_date': fields.date ('Date of Diagnosis'),
		'healed_date' : fields.date ('Healed'),
		'is_active' : fields.boolean ('Active disease'),
		'age': fields.integer ('Age when diagnosed',help='Patient age at the moment of the diagnosis. Can be estimative'),
		'pregnancy_warning': fields.boolean ('Pregnancy warning'),
		'weeks_of_pregnancy' : fields.integer ('Contracted in pregnancy week #'),
		'is_allergy' : fields.boolean ('Allergic Disease'),
		'allergy_type' : fields.selection ([
			('da','Drug Allergy'),
			('fa','Food Allergy'),
			('ma','Misc Allergy'),
			('mc','Misc Contraindication'),
			], 'Allergy type', select=True),		
		'pcs_code' : fields.many2one ('medical.procedure','Code', help="Procedure code, for example, ICD-10-PCS Code 7-character string"),
		'treatment_description' : fields.char ('Treatment Description',size=128),
		'date_start_treatment' : fields.date ('Start of treatment'),
		'date_stop_treatment' : fields.date ('End of treatment'),
		'status' : fields.selection ([
			('c','chronic'),
			('s','status quo'),
			('h','healed'),
			('i','improving'),
			('w','worsening'),
			], 'Status of the disease', select=True),
		'extra_info' : fields.text ('Extra Info'),
		}

	_order = 'is_active desc, disease_severity desc, is_infectious desc, is_allergy desc, diagnosed_date desc'

	_defaults = {
		'is_active': lambda *a : True,
                }

patient_disease_info ()

# MEDICATION DOSAGE 
class medication_dosage (osv.osv):
	_name = "medical.medication.dosage"
	_description = "Medicament Common Dosage combinations"
	_columns = {
		'name': fields.char ('Frequency', size=256, help='Common frequency name'),
		'code': fields.char ('Code', size=64, help='Dosage Code, such as SNOMED, 229798009 = 3 times per day'),
		'abbreviation' : fields.char  ('Abbreviation', size=64, help='Dosage abbreviation, such as tid in the US or tds in the UK'),
		}

medication_dosage ()

# MEDICATION TEMPLATE
# TEMPLATE USED IN MEDICATION AND PRESCRIPTION ORDERS

class medication_template (osv.osv):

	_name = "medical.medication.template"
	_description = "Template for medication"
	_columns = {
		'medicament' : fields.many2one ('medical.medicament','Medicament',help="Prescribed Medicament"),
		'indication' : fields.many2one ('medical.pathology','Indication', help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic."),
		'dose' : fields.integer ('Dose',help="Amount of medication (eg, 250 mg ) each time the patient takes it"),
		'dose_unit' : fields.many2one ('medical.dose.unit','dose unit', help="Unit of measure for the medication to be taken"),
		'route' : fields.many2one ('medical.drug.route','Administration Route',help="HL7 or other standard drug administration route code."),
		'form' : fields.many2one ('medical.drug.form','Form',help="Drug form, such as tablet or gel"),
		'qty' : fields.integer ('x',help="Quantity of units (eg, 2 capsules) of the medicament"),
		'common_dosage' : fields.many2one ('medical.medication.dosage','Frequency',help="Common / standard dosage frequency for this medicament"),
		'frequency' : fields.integer ('Frequency', help="Time in between doses the patient must wait (ie, for 1 pill each 8 hours, put here 8 and select 'hours' in the unit field"),
		'frequency_unit' : fields.selection ([
			('seconds','seconds'),
			('minutes','minutes'),
			('hours','hours'),
			('days','days'),
			('weeks','weeks'),
			('wr','when required'),
			], 'unit', select=True),
		'admin_times' : fields.char  ('Admin hours', size=128, help='Suggested administration hours. For example, at 08:00, 13:00 and 18:00 can be encoded like 08 13 18'),
		'duration' : fields.integer ('Treatment duration',help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately"),
		'duration_period' : fields.selection([
                                ('minutes','minutes'),
                                ('hours','hours'),
				('days','days'),
				('months','months'),
				('years','years'),
				('indefinite','indefinite'),
                               ], 'Treatment period',help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately", select=True),
		'start_treatment' : fields.datetime ('Start of treatment'),
		'end_treatment' : fields.datetime ('End of treatment'),
		}


medication_template ()		




# PATIENT MEDICATION TREATMENT
class patient_medication (osv.osv):

	_name = "medical.patient.medication"
	_inherit = "medical.medication.template"
	_description = "Patient Medication"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID',readonly=True),
		'doctor' : fields.many2one('medical.physician','Physician', help="Physician who prescribed the medicament"),
		'is_active' : fields.boolean('Active',help="Check this option if the patient is currently taking the medication"),
		'discontinued' :  fields.boolean('Discontinued'),
		'course_completed' : fields.boolean('Course Completed'),
		'discontinued_reason' : fields.char ('Reason for discontinuation', size=128, help="Short description for discontinuing the treatment"),
		'adverse_reaction' : fields.text ('Adverse Reactions',help="Specific side effects or adverse reactions that the patient experienced"),
		'notes' : fields.text ('Extra Info'),
		'patient_id' : fields.many2one('medical.patient','Patient'),		
		}

	_defaults = {
		'is_active': lambda *a : True,
		'start_treatment': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                'frequency_unit': lambda *a: 'hours',
                'duration_period': lambda *a: 'days',
                'qty': lambda *a: 1,                                                              
                }
	
patient_medication ()



# PATIENT EVALUATION

class patient_evaluation (osv.osv):

# Kludge to get patient ID when using one2many fields.
	def onchange_evaluation_date (self, cr, uid, ids,name, patient):
		if not name:
#			pdb.set_trace()
			return {'value': {'name': patient}}


	_name = "medical.patient.evaluation"
	_description = "evaluation"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID'),
                'evaluation_date' : fields.many2one ('medical.appointment','Evaluation Date', help="Enter or select the date / ID of the appointment related to this evaluation"),
		'evaluation_endtime' : fields.datetime ('End of Evaluation'),
		'next_evaluation' : fields.many2one ('medical.appointment','Next Appointment'),
		'user_id' : fields.many2one ('res.users','Doctor', readonly=True),
		'derived_from' : fields.many2one('medical.physician','Derived from Doctor', help="Physician who escalated / derived the case"), 
		'derived_to' : fields.many2one('medical.physician','Derived to Doctor', help="Physician to whom escalate / derive the case"), 
		'evaluation_type' : fields.selection([
                                ('a','Ambulatory'),
                                ('e','Emergency'),
                                ('i','Inpatient'),
                                ('pa','Pre-arraganged appointment'),
                                ('pc','Periodic control'),
			        ('p','Phone call'),
			        ('t','Telemedicine'),
                                ], 'Evaluation Type', select=True),
		'chief_complaint' : fields.char ('Chief Complaint', size=128,help='Chief Complaint'),
		'notes_complaint' : fields.text ('Complaint details'),
		'glycemia' : fields.float('Glycemia', help="Last blood glucose level. Can be approximative."),
		'hba1c' : fields.float('Glycated Hemoglobin', help="Last Glycated Hb level. Can be approximative."),
		'cholesterol_total' : fields.integer ('Last Cholesterol',help="Last cholesterol reading. Can be approximative"),
		'hdl' : fields.integer ('Last HDL',help="Last HDL Cholesterol reading. Can be approximative"),
		'ldl' : fields.integer ('Last LDL',help="Last LDL Cholesterol reading. Can be approximative"),
		'tag' : fields.integer ('Last TAGs',help="Triacylglycerols (triglicerides) level. Can be approximative"),
		'systolic' : fields.integer('Systolic Pressure'),
		'diastolic' : fields.integer('Diastolic Pressure'),
		'bpm' : fields.integer ('Heart Rate',help="Heart rate expressed in beats per minute"),
		'respiratory_rate' : fields.integer ('Respiratory Rate',help="Respiratory rate expressed in breaths per minute"),
		'osat' : fields.integer ('Oxygen Saturation',help="Oxygen Saturation (arterial)."),
		'malnutrition' : fields.boolean ('Malnutrition', help="Check this box if the patient show signs of malnutrition. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Moderate protein-energy malnutrition, E44.0 in ICD-10 encoding"),
		'dehydration' : fields.boolean ('Dehydration', help="Check this box if the patient show signs of dehydration. If not associated to a disease, please encode the correspondent disease on the patient disease history. For example, Volume Depletion, E86 in ICD-10 encoding"),
		'temperature' : fields.float('Temperature (celsius)'),
		'weight' : fields.float('Weight (kg)'),
		'height' : fields.float('Height (cm)'),
		'bmi' : fields.float('Body Mass Index'),
		'head_circumference' : fields.float('Head Circumference',help="Head circumference"),		
		'abdominal_circ' : fields.float('Abdominal Circumference'),
		'edema' : fields.boolean ('Edema', help="Please also encode the correspondent disease on the patient disease history. For example,  R60.1 in ICD-10 encoding"),
		'petechiae' : fields.boolean ('Petechiae'),
		'hematoma' : fields.boolean ('Hematomas'),
		'cyanosis' : fields.boolean ('Cyanosis', help="If not associated to a disease, please encode it on the patient disease history. For example,  R23.0 in ICD-10 encoding"),
		'acropachy' : fields.boolean ('Acropachy', help="Check if the patient shows acropachy / clubbing"),		
		'nystagmus' : fields.boolean ('Nystagmus', help="If not associated to a disease, please encode it on the patient disease history. For example,  H55 in ICD-10 encoding"),
		'miosis' : fields.boolean ('Miosis', help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding" ),
		'mydriasis' : fields.boolean ('Mydriasis', help="If not associated to a disease, please encode it on the patient disease history. For example,  H57.0 in ICD-10 encoding"),
		'cough' : fields.boolean ('Cough', help="If not associated to a disease, please encode it on the patient disease history."),
		'palpebral_ptosis' : fields.boolean ('Palpebral Ptosis', help="If not associated to a disease, please encode it on the patient disease history"),
		'arritmia' : fields.boolean ('Arritmias', help="If not associated to a disease, please encode it on the patient disease history"),		
		'heart_murmurs' : fields.boolean ('Heart Murmurs'),
		'heart_extra_sounds' : fields.boolean ('Heart Extra Sounds', help="If not associated to a disease, please encode it on the patient disease history"),		
		'jugular_engorgement' : fields.boolean ('Tremor', help="If not associated to a disease, please encode it on the patient disease history"),
		'ascites' : fields.boolean ('Ascites', help="If not associated to a disease, please encode it on the patient disease history"),	
		'lung_adventitious_sounds' : fields.boolean ('Lung Adventitious sounds', help="Crackles, wheezes, ronchus.."),
		'bronchophony' : fields.boolean ('Bronchophony'),
		'increased_fremitus' : fields.boolean ('Increased Fremitus'),
		'decreased_fremitus' : fields.boolean ('Decreased Fremitus'),							
		'jaundice' : fields.boolean ('Jaundice', help="If not associated to a disease, please encode it on the patient disease history"),		
		'lynphadenitis' : fields.boolean ('Linphadenitis', help="If not associated to a disease, please encode it on the patient disease history"),
		'breast_lump' : fields.boolean ('Breast Lumps'),
		'breast_asymmetry' : fields.boolean ('Breast Asymmetry'),
		'nipple_inversion' : fields.boolean ('Nipple Inversion'),
		'nipple_discharge' : fields.boolean ('Nipple Discharge'),
		'peau_dorange' : fields.boolean ('Peau d orange',help="Check if the patient has prominent pores in the skin of the breast" ),				
		'gynecomastia' : fields.boolean ('Gynecomastia'),

		'masses' : fields.boolean ('Masses', help="Check when there are findings of masses / tumors / lumps"),
		'hypotonia' : fields.boolean ('Hypotonia', help="Please also encode the correspondent disease on the patient disease history."),
		'hypertonia' : fields.boolean ('Hypertonia', help="Please also encode the correspondent disease on the patient disease history."),
		'pressure_ulcers' : fields.boolean ('Pressure Ulcers', help="Check when Decubitus / Pressure ulcers are present"),		
		'goiter' : fields.boolean ('Goiter'),		
		'alopecia' : fields.boolean ('Alopecia', help="Check when alopecia - including androgenic - is present"),		
		'xerosis' : fields.boolean ('Xerosis'),				
		'erithema' : fields.boolean ('Erithema', help="Please also encode the correspondent disease on the patient disease history."),
		'loc' : fields.integer('Level of Consciousness', help="Level of Consciousness - on Glasgow Coma Scale :  1=coma - 15=normal"),
		'loc_eyes' : fields.integer('Level of Consciousness - Eyes', help="Eyes Response - Glasgow Coma Scale - 1 to 4"),
		'loc_verbal' : fields.integer('Level of Consciousness - Verbal', help="Verbal Response - Glasgow Coma Scale - 1 to 5"),
		'loc_motor' : fields.integer('Level of Consciousness - Motor', help="Motor Response - Glasgow Coma Scale - 1 to 6"),		
		'violent' : fields.boolean ('Violent Behaviour', help="Check this box if the patient is agressive or violent at the moment"),
		'mood' : fields.selection([
                                ('n','Normal'),
                                ('s','Sad'),
                                ('f','Fear'),
                                ('r','Rage'),
                                ('h','Happy'),
                                ('d','Disgust'),
                                ('e','Euphoria'),
                                ('fl','Flat'),
                                ], 'Mood', select=True),
                                
		'orientation' : fields.boolean ('Orientation', help="Check this box if the patient is disoriented in time and/or space"),
		'memory' : fields.boolean ('Memory', help="Check this box if the patient has problems in short or long term memory"),
		'knowledge_current_events' : fields.boolean ('Knowledge of Current Events', help="Check this box if the patient can not respond to public notorious events"),
		'judgment' : fields.boolean ('Jugdment', help="Check this box if the patient can not interpret basic scenario solutions"),
		'abstraction' : fields.boolean ('Abstraction', help="Check this box if the patient presents abnormalities in abstract reasoning"),
		'vocabulary' : fields.boolean ('Vocabulary', help="Check this box if the patient lacks basic intelectual capacity, when she/he can not describe elementary objects"),
		'calculation_ability' : fields.boolean ('Calculation Ability',help="Check this box if the patient can not do simple arithmetic problems"),
		'object_recognition' : fields.boolean ('Object Recognition', help="Check this box if the patient suffers from any sort of gnosia disorders, such as agnosia, prosopagnosia ..."),
		'praxis' : fields.boolean ('Praxis', help="Check this box if the patient is unable to make voluntary movements"),
		'diagnosis' : fields.many2one ('medical.pathology','Presumptive Diagnosis', help="Presumptive Diagnosis"),
		'info_diagnosis' : fields.text('Presumptive Diagnosis: Extra Info'),
		'directions' : fields.text('Plan'),
		'actions' : fields.one2many('medical.directions', 'name', 'Actions'),
		'symptom_pain' : fields.boolean ('Pain'),
		'symptom_pain_intensity' : fields.integer ('Pain intensity', help="Pain intensity from 0 (no pain) to 10 (worst possible pain)"),
		'symptom_arthralgia' : fields.boolean ('Arthralgia'),
		'symptom_myalgia' : fields.boolean ('Myalgia'),
		'symptom_abdominal_pain' : fields.boolean ('Abdominal Pain'),
		'symptom_cervical_pain' : fields.boolean ('Cervical Pain'),
		'symptom_thoracic_pain' : fields.boolean ('Thoracic Pain'),
		'symptom_lumbar_pain' : fields.boolean ('Lumbar Pain'),		
		'symptom_pelvic_pain' : fields.boolean ('Pelvic Pain'),
		'symptom_headache' : fields.boolean ('Headache'),
		'symptom_odynophagia' : fields.boolean ('Odynophagia'),
		'symptom_sore_throat' : fields.boolean ('Sore throat'),
		'symptom_otalgia' : fields.boolean ('Otalgia'),
		'symptom_tinnitus' : fields.boolean ('Tinnitus'),
		'symptom_ear_discharge' : fields.boolean ('Ear Discharge'),		
		'symptom_hoarseness' : fields.boolean ('Hoarseness'),		
		'symptom_chest_pain' : fields.boolean ('Chest Pain'),
		'symptom_chest_pain_excercise' : fields.boolean ('Chest Pain on excercise only'),
		'symptom_orthostatic_hypotension' : fields.boolean ('Orthostatic hypotension', help="If not associated to a disease,please encode it on the patient disease history. For example,  I95.1 in ICD-10 encoding"),		
		'symptom_astenia' : fields.boolean ('Astenia'),
		'symptom_anorexia' : fields.boolean ('Anorexia'),
		'symptom_weight_change' : fields.boolean ('Sudden weight change'),
		'symptom_abdominal_distension' : fields.boolean ('Abdominal Distension'),
		'symptom_hemoptysis' : fields.boolean ('Hemoptysis'),
		'symptom_hematemesis' : fields.boolean ('Hematemesis'),
		'symptom_epistaxis' : fields.boolean ('Epistaxis'),
		'symptom_gingival_bleeding' : fields.boolean ('Gingival Bleeding'),		
		'symptom_rinorrhea' : fields.boolean ('Rinorrhea'),						
		'symptom_nausea' : fields.boolean ('Nausea'),
		'symptom_vomiting' : fields.boolean ('Vomiting'),				
		'symptom_dysphagia' : fields.boolean ('Dysphagia'),		
		'symptom_polydipsia' : fields.boolean ('Polydipsia'),
		'symptom_polyphagia' : fields.boolean ('Polyphagia'),
		'symptom_polyuria' : fields.boolean ('Polyuria'),
		'symptom_nocturia' : fields.boolean ('Nocturia'),
		'symptom_vesical_tenesmus' : fields.boolean ('Vesical Tenesmus'),
		'symptom_pollakiuria' : fields.boolean ('Pollakiuiria'),
		'symptom_dysuria' : fields.boolean ('Dysuria'),		
		'symptom_stress' : fields.boolean ('Stressed-out'),
		'symptom_mood_swings' : fields.boolean ('Mood Swings'),		
		'symptom_pruritus' : fields.boolean ('Pruritus'),
		'symptom_insomnia' : fields.boolean ('Insomnia'),
		'symptom_disturb_sleep' : fields.boolean ('Disturbed Sleep'),		
		'symptom_dyspnea' : fields.boolean ('Dyspnea'),
		'symptom_orthopnea' : fields.boolean ('Orthopnea'),		
		'symptom_amnesia' : fields.boolean ('Amnesia'),
		'symptom_paresthesia' : fields.boolean ('Paresthesia'),		
		'symptom_paralysis' : fields.boolean ('Paralysis'),
		'symptom_syncope' : fields.boolean ('Syncope'),
		'symptom_dizziness' : fields.boolean ('Dizziness'),
		'symptom_vertigo' : fields.boolean ('Vertigo'),				
		'symptom_eye_glasses' : fields.boolean ('Eye glasses',help="Eye glasses or contact lenses"),
		'symptom_blurry_vision' : fields.boolean ('Blurry vision'),
		'symptom_diplopia' : fields.boolean ('Diplopia'),
		'symptom_photophobia' : fields.boolean ('Photophobia'),
		'symptom_dysmenorrhea' : fields.boolean ('Dysmenorrhea'),
		'symptom_amenorrhea' : fields.boolean ('Amenorrhea'),
		'symptom_metrorrhagia' : fields.boolean ('Metrorrhagia'),
		'symptom_menorrhagia' : fields.boolean ('Menorrhagia'),
		'symptom_vaginal_discharge' : fields.boolean ('Vaginal Discharge'),		
		'symptom_urethral_discharge' : fields.boolean ('Urethral Discharge'),		
		'symptom_diarrhea' : fields.boolean ('Diarrhea'),
		'symptom_constipation' : fields.boolean ('Constipation'),
		'symptom_rectal_tenesmus' : fields.boolean ('Rectal Tenesmus'),
		'symptom_melena' : fields.boolean ('Melena'),
		'symptom_proctorrhagia' : fields.boolean ('Proctorrhagia'),		
		'symptom_xerostomia' : fields.boolean ('Xerostomia'),
		'symptom_sexual_dysfunction' : fields.boolean ('Sexual Dysfunction'),
		'notes' : fields.text ('Notes'),
	}

	_defaults = {
                'loc_eyes': lambda *a: 4,
                'loc_verbal': lambda *a: 5,
                'loc_motor': lambda *a: 6,
		'evaluation_type': lambda *a: 'pa',
		'user_id': lambda obj, cr, uid, context: uid,
		'name': lambda self, cr, uid, c: c.get('name', False),
		
        }


	def onchange_height_weight (self, cr, uid, ids, height, weight):
		if height:
			v = {'bmi':weight/((height/100)**2)}
		else:
			v = {'bmi':0}

		return {'value': v}	
				
	def onchange_loc (self, cr, uid, ids, loc_motor, loc_eyes, loc_verbal):
		v = {'loc':loc_motor + loc_eyes + loc_verbal}
		return {'value': v}	



patient_evaluation ()


# PATIENT DIRECTIONS (to be used also in surgeries if using standards like ICD10-PCS)

class directions (osv.osv):
	_name = "medical.directions"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID', readonly=True),
		'procedure' : fields.many2one ('medical.procedure', 'Procedure'),
		'comments' : fields.char ('Comments', size=128),
		}

directions ()





# PRESCRIPTION ORDER

class patient_prescription_order (osv.osv):

	_name = "medical.prescription.order"
	_description = "prescription order"

		
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID'),
		'prescription_id' : fields.char ('Prescription ID', size=128,required=True, help='Type in the ID of this prescription'),
		'prescription_date' : fields.datetime ('Prescription Date'),
		'user_id' : fields.many2one ('res.users','Prescribing Doctor', readonly=True),
		'pharmacy' : fields.many2one ('res.partner', 'Pharmacy'),
		'prescription_line' : fields.one2many ('medical.prescription.line', 'name', 'Prescription line'),
		'notes' : fields.text ('Prescription Notes'),
		}

	_defaults = {
                'prescription_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'user_id': lambda obj, cr, uid, context: uid,		
		'prescription_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'medical.prescription'),
                }


patient_prescription_order ()

		
# PRESCRIPTION LINE
class prescription_line (osv.osv):

	_name = "medical.prescription.line"
	_description = "Basic prescription object"
	_inherit = "medical.medication.template"
	_columns = {
		'name' : fields.many2one ('medical.prescription.order','Prescription ID'),	
		'review' : fields.datetime ('Review'),
		'quantity' : fields.integer ('Quantity'),
		'refills' : fields.integer ('Refills #'),
		'allow_substitution' : fields.boolean('Allow substitution'),  
		'short_comment' : fields.char ('Comment', size=128, help='Short comment on the specific drug'),
		'prnt' : fields.boolean ('Print', help='Check this box to print this line of the prescription.'),
		}
	_defaults = {
                'qty': lambda *a: 1,
                'duration_period': lambda *a: 'days',
                'frequency_unit': lambda *a: 'hours',
                'quantity' : lambda *a: 1,
                'prnt': lambda *a: True,                               
                }
		
prescription_line ()



# PATIENT VACCINATION INFORMATION

class vaccination (osv.osv):
	def _check_vaccine_expiration_date(self,cr,uid,ids):
		vaccine=self.browse(cr,uid,ids[0])
		if vaccine:
			if vaccine.vaccine_expiration_date < vaccine.date:
				return False
		return True

	def onchange_vaccination_expiration_date(self, cr, uid, ids, vaccine_date, vaccination_expiration_date):
		if vaccination_expiration_date and vaccine_date:
			if vaccination_expiration_date < vaccine_date:
				v = {'vaccine_expiration_date':''}
				exp_message = "EXPIRED VACCINE !! "+ vaccination_expiration_date + "\nPlease Dispose it !!"
				return {'value': v,'warning':{'title':'warning','message': exp_message}}	
	

	_name = "medical.vaccination"
	_columns = {
		'name' : fields.many2one ('medical.patient','Patient ID', readonly=True),
		'vaccine' : fields.many2one ('product.product','Name', domain=[('is_vaccine', '=', "1")], help="Vaccine Name. Make sure that the vaccine (product) has all the proper information at product level. Information such as provider, supplier code, tracking number, etc.. This information must always be present. If available, please copy / scan the vaccine leaflet and attach it to this record"),
		'vaccine_expiration_date' : fields.date ('Expiration date'),
		'vaccine_lot' : fields.char ('Lot Number',size=128,help="Please check on the vaccine (product) production lot number and tracking number when available !"),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center where the patient is being or was vaccinated"),
		'date' : fields.datetime ('Date'),
		'dose' : fields.integer ('Dose Number'),
		'observations' : fields.char ('Observations', size=128),
		}
	_defaults = {
                'dose': lambda *a: 1,
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		}

	_constraints = [
        (_check_vaccine_expiration_date, 'WARNING !! EXPIRED VACCINE. PLEASE INFORM THE LOCAL HEALTH AUTHORITIES AND DO NOT USE IT !!', ['vaccine_expiration_date'])
	] 
        _sql_constraints = [
                ('dose_unique', 'unique (name,dose,vaccine)', 'This vaccine dose has been given already to the patient ')
                ]


vaccination ()


# HEALTH CENTER / HOSPITAL INFRASTRUCTURE


class hospital_building (osv.osv):
	_name = "medical.hospital.building"
	_columns = {
		'name' : fields.char ('Name', size=128, help="Name of the building within the institution"),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'code' : fields.char ('Code', size=64),
		'extra_info' : fields.text ('Extra Info'),
		}
hospital_building ()

class hospital_unit (osv.osv):
	_name = "medical.hospital.unit"
	_columns = {
		'name' : fields.char ('Name', size=128, help="Name of the unit, eg Neonatal, Intensive Care, ..."),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'code' : fields.char ('Code', size=64),
		'extra_info' : fields.text ('Extra Info'),
		}
hospital_unit ()

class hospital_ward (osv.osv):
	_name = "medical.hospital.ward"
	_columns = {
		'name' : fields.char ('Name', size=128, help="Ward / Room code"),
		'institution' : fields.many2one ('res.partner','Institution', domain=[('is_institution', '=', "1")],help="Medical Center"),
		'building' : fields.many2one ('medical.hospital.building','Building'),
		'floor' : fields.integer ('Floor Number'),
		'unit' : fields.many2one ('medical.hospital.unit','Unit'),
		'private' : fields.boolean ('Private',help="Check this option for private room"),
		'bio_hazard' : fields.boolean ('Bio Hazard',help="Check this option if there is biological hazard"),
		'number_of_beds' : fields.integer ('Number of beds',help="Number of patients per ward"),
		'telephone' : fields.boolean ('Telephone access'),
		'ac' : fields.boolean ('Air Conditioning'),
		'private_bathroom' : fields.boolean ('Private Bathroom'),
		'guest_sofa' : fields.boolean ('Guest sofa-bed'),
		'tv' : fields.boolean ('Television'),
		'internet' : fields.boolean ('Internet Access'),
		'refrigerator' : fields.boolean ('Refrigetator'),
		'microwave' : fields.boolean ('Microwave'),
		'gender' : fields.selection ((('men','Men Ward'),('women','Women Ward'),('unisex','Unisex')),'Gender', required=True),
		'state': fields.selection((('beds_available','Beds available'),('full','Full'),('na','Not available')),'Status'),
		'extra_info' : fields.text ('Extra Info'),
		}

	_defaults = {
		'gender': lambda *a: 'unisex',
                'number_of_beds': lambda *a: 1,
		}

hospital_ward ()

class hospital_bed (osv.osv):

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		rec_name = 'name'
		res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
		return res

	_name = "medical.hospital.bed"
	_columns = {
		'name' : fields.many2one ('product.product','Bed', domain=[('is_bed', '=', "1")], help="Bed Number"),
		'ward' : fields.many2one ('medical.hospital.ward','Ward',help="Ward or room"),
		'bed_type' : fields.selection((('gatch','Gatch Bed'),('electric','Electric'),('stretcher','Stretcher'),('low','Low Bed'),('low_air_loss','Low Air Loss'),('circo_electric','Circo Electric'),('clinitron','Clinitron')),'Bed Type', required=True),
		'telephone_number' : fields.char ('Telephone Number',size=128, help="Telephone number / Extension"),
		'extra_info' : fields.text ('Extra Info'),
		'state': fields.selection((('free','Free'),('reserved','Reserved'),('occupied','Occupied'),('na','Not available')),'Status'),
		}

	_defaults = {
                'bed_type': lambda *a: 'gatch',
		}

hospital_bed ()



