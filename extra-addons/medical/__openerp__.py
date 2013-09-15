# -*- encoding: utf-8 -*-
{

	'name' : 'Medical : Free Health and Hospital Information System',  
	'version' : '1.0',
	'author' : 'Thymbra',
	'category' : 'Generic Modules/Others',
	'depends' : ['base','sale','purchase','account','product'],
	'description' : """

About Medical
-------------
Medical is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for openERP.

Medical provides a free universal Health and Hospital Information System, so doctors and institutions all over the world, specially in developing countries will benefit from a centralized, high quality, secure and scalable system.


Medical at a glance:


    * Strong focus in family medicine and Primary Health Care

    * Major interest in Socio-economics (housing conditions, substance abuse, education...)

    * Diseases and Medical procedures standards (like ICD-10 / ICD-10-PCS ...)

    * Patient Genetic and Hereditary risks : Over 4200 genes related to diseases (NCBI / Genecards)

    * Epidemiological and other statistical reports

    * 100% paperless patient examination and history taking

    * Patient Administration (creation, evaluations / consultations, history ... )

    * Doctor Administration

    * Lab Administration

    * Medicine / Drugs information (vademécum)

    * Medical stock and supply chain management

    * Hospital Financial Administration

    * Designed with industry standards in mind

    * Open Source : Licensed under GPL 



Most of the action should occur at sourceforge, so check the main page http://sourceforge.net/projects/medical for the latest news and developer releases. 

""",
	"website" : "http://medical.sourceforge.net",
	"init_xml" : [],
	"demo_xml" : ["demo/medical_demo.xml"],
# Use the following line for English

#	"update_xml" : ["medical_view.xml","medical_report.xml", "data/medical_sequences.xml","security/medical_security.xml","security/ir.model.access.csv"],

	"update_xml" : ["medical_view.xml","medical_installer.xml","medical_report.xml", "data/medical_sequences.xml","security/medical_security.xml","security/ir.model.access.csv","data/ethnic_groups.xml","data/occupations.xml","data/dose_units.xml","data/HL7_drug_administration_routes.xml","data/medicament_form.xml","data/snomed_frequencies.xml","data/medicament_categories.xml","data/WHO_list_of_essential_medicines.xml","data/WHO_medicaments.xml","data/medical_specialties.xml"],

# Use translation data files for diseases in the other modules.

# Use the following line for spanish and comment the prior line.
#       "update_xml" : ["medical_view.xml","medical_installer.xml","medical_report.xml", "data/medical_sequences.xml","security/medical_security.xml","security/ir.model.access.csv","data/ethnic_groups_es.xml","data/occupations_es.xml","data/dose_units_es.xml","data/HL7_drug_administration_routes.xml","data/medicament_form_es.xml","data/snomed_frequencies_es.xml","data/medicament_categories_es.xml","data/WHO_list_of_essential_medicines_es.xml","data/WHO_medicaments_es.xml","data/medical_specialties_es.xml"],


#	"update_xml" : ["medical_view.xml","security/medical_security.xml","security/ir.model.access.csv"],

#	"update_xml" : ["medical_view.xml","security/medical_security.xml","security/ir.model.access.csv","data/ethnic_groups.xml","data/occupations.xml","data/genetic_risks.xml","data/dose_units.xml","data/HL7_drug_administration_routes.xml","data/medicament_categories.xml","data/WHO_list_of_essential_medicines.xml","data/WHO_medicaments.xml","data/disease_categories.xml","data/diseases.xml"],

# Use the following line for German
#	"update_xml" : ["medical_view.xml","security/medical_security.xml","security/ir.model.access.csv","data/disease_categories_de.xml","data/diseases_de.xml","data/ethnic_groups.xml","data/occupations.xml","data/icmp_ops_de.xml","data/genetic_risks.xml","data/dose_units.xml","data/medicament_categories.xml","data/WHO_list_of_essential_medicines.xml","data/WHO_medicaments.xml","data/medical_specialties.xml"],

# Use the following line for Vietnamese

#	"update_xml" : ["medical_view.xml","medical_report.xml", "data/medical_sequences.xml","security/medical_security.xml","security/ir.model.access.csv","data/ethnic_groups_vi.xml","data/occupations_vi.xml","data/dose_units.xml","data/HL7_drug_administration_routes_vi.xml","data/medicament_form_vi.xml","data/snomed_frequencies_vi.xml","data/medicament_categories_vi.xml","data/WHO_list_of_essential_medicines.xml","data/WHO_medicaments.xml","data/medical_specialties.xml"],


#	"update_xml" : ["medical_view.xml"],
	"active": False 
}
