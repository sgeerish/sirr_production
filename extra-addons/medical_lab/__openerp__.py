# -*- encoding: utf-8 -*-
{

	'name' : 'Medical : Laboratory',  
	'version' : '1.0',
	'author' : 'Thymbra',
	'category' : 'Generic Modules/Others',
	'depends' : ['medical'],
	'description' : """

This modules includes lab tests: Values, reports and PoS.


""",
	"website" : "http://medical.sourceforge.net",
	"init_xml" : [],
	"update_xml" : ["security/ir.model.access.csv", "medical_lab_view.xml", "medical_lab_report.xml", "data/medical_lab_sequences.xml", "data/lab_test_data.xml","wizard/create_lab_test.xml"],
	"active": False 
}
