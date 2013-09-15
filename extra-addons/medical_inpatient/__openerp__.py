# -*- encoding: utf-8 -*-
{

	'name' : 'Medical Inpatient : Hospitalization module for Medical',  
	'version' : '1.0',
	'author' : 'Thymbra',
	'category' : 'Generic Modules/Others',
	'depends' : ['medical'],
	'description' : """
This module will hold all the processes related to Inpatient (Patient hospitalization and bed assignment )

- Patient Registration
- Bed reservation
- Hospitalization
- Nursing Plan
- Discharge Plan
- Reporting

""",
	"website" : "http://medical.sourceforge.net",
	"init_xml" : [],

	"update_xml" : ["medical_inpatient_view.xml", "data/medical_inpatient_sequence.xml","security/ir.model.access.csv"],
	"active": False 
}
