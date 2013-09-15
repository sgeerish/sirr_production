# -*- encoding: utf-8 -*-
{

	'name' : 'Medical : Lifestyle',  
	'version' : '1.0',
	'author' : 'Thymbra',
	'category' : 'Generic Modules/Others',
	'depends' : ['medical'],
	'description' : """

Gathers information about the habits and sexuality of the patient

- Eating habits and diets
- Sleep patterns
- Drug / alcohol addictions
- Physical activity (workout / excercise )
- Sexuality and sexual behaviours


""",
	"website" : "http://medical.sourceforge.net",
	"init_xml" : [],
	"update_xml" : ["medical_lifestyle_view.xml","data/recreational_drugs.xml","security/ir.model.access.csv"],
	"active": False 
}
