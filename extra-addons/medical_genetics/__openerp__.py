# -*- encoding: utf-8 -*-
{

	'name' : 'Medical : Genetics',  
	'version' : '1.0',
	'author' : 'Thymbra',
	'category' : 'Generic Modules/Others',
	'depends' : ['medical'],
	'description' : """

Family history and genetic risks

The module includes hereditary risks, family history and genetic disorders.

In this module we include the NCBI and Genecard information, more than 4200 genes associated to diseases


""",
	"website" : "http://medical.sourceforge.net",
	"init_xml" : [],
	"update_xml" : ["medical_genetics_view.xml","data/genetic_risks.xml","security/ir.model.access.csv"],
	"active": False 
}
