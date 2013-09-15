# -*- encoding: utf-8 -*-
{

	'name' : 'Medical : Gynecology and obstetrics module',  
	'version' : '1.0',
	'author' : 'Thymbra',
	'category' : 'Generic Modules/Others',
	'depends' : ['medical'],
	'description' : """

This module includes :

- Gynecological Information
- Obstetric information 
- Perinatal Information and monitoring
- Puerperium

""",
	"website" : "http://medical.sourceforge.net",
	"init_xml" : [],
	"update_xml" : ["medical_gyneco_view.xml","security/ir.model.access.csv"],
	"active": False 
}
