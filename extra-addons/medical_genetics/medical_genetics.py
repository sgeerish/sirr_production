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


from osv import fields, osv


class genetic_risk (osv.osv):
	_name= "medical.genetic.risk"
	_description= "Genetic Risks"
	_columns = {
		'name' : fields.char ('Official Symbol', size=16),
		'long_name' : fields.char ('Official Long Name', size=256),
		'gene_id' : fields.char ('Gene ID', size=8, help="default code from NCBI Entrez database."),
		'chromosome' : fields.char ('Affected Chromosome', size=2, help="Name of the affected chromosome"),
		'location' : fields.char ('Location', size=32, help="Locus of the chromosome"),
		'dominance' : fields.selection([
                                ('d','dominant'),
                                ('r','recessive'),
                                ], 'Dominance', select=True),		
		'info' : fields.text ('Information', size=128, help="Name of the protein(s) affected"),
	}


	def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
        	args2 = args[:]
        	if name:
            		args += [('name', operator, name)]
            		args2 += [('long_name', operator, name)]
        	ids = self.search(cr, uid, args, limit=limit)
        	ids += self.search(cr, uid, args2, limit=limit)
        	res = self.name_get(cr, uid, ids, context)
        	return res

genetic_risk ()




class family_diseases (osv.osv):
	_name = "medical.family.diseases"
	_description = "Family Diseases"
	_columns = {
		'name' : fields.many2one ('medical.pathology', 'Disease'),
		'xory' : fields.selection([
                                ('m','Maternal'),
                                ('f','Paternal'),
                                ], 'Maternal or Paternal'),

		'relative' : fields.selection([
                                ('m','Mother'),
                                ('a','Father'),
                                ('b','Brother'),
                                ('s','Sister'),
                                ('au','Aunt'),
                                ('u','Uncle'),
                                ('ne','Nephew'),
                                ('ni','Niece'),
                                ('gf','Grandfather'),
                                ('gm','Grandmother'),
                                ('c','Cousin'),
                                ], 'Relative', help="First degree = siblings, mother and father; second degree = Uncles, nephews and Nieces; third degree = Grandparents and cousins", select=True),


		}

family_diseases ()



# Add to the Medical patient_data class (medical.patient) the genetic and family risks


class medical_patient (osv.osv):
	_name = "medical.patient"
	_inherit = "medical.patient"
	_columns = {
		
		'genetic_risks' : fields.many2many('medical.genetic.risk','patient_genetic_risks_rel','patient_id','genetic_risk_id','Genetic Risks'),
		'family_history' : fields.many2many ('medical.family.diseases', 'patient_familyhist_rel','patient_id','pathology_id', 'Family History'),
		
	}

medical_patient ()
		
