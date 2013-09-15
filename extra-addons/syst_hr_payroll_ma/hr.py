import netsvc
from osv import fields, osv
import pooler
from tools.translate import _
import time


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'matricule' : fields.char('Matricule', size=64),
        'cin' : fields.char('CIN', size=64),
        'date': fields.date('Date entree', help='Cette date est requipe pour le calcule de la prime d\'anciennete'),
        'anciennete': fields.boolean('Prime anciennete', help='Est ce que cet employe benificie de la prime d\'anciennete'),
        'mode_reglement' : fields.selection([('virement', 'Virement'), ('cheque', 'Cheque'), ('espece', 'Espece'), ], 'Mode De Reglement'),
        'bank' : fields.char('Banque', size=128),
        'compte' : fields.char('Compte bancaire', size=128),
        'chargefam' : fields.integer('Nombre de personnes a charge'),
        'logement': fields.float('Abattement Fr Logement'), 
        'affilie':fields.boolean('Affilie', help='Est ce qu on va calculer les cotisations pour cet employe'),
        'address_home' : fields.char('Adresse Personnelle', size=128),
        'address' : fields.char('Adresse Professionnelle', size=128),
        'phone_home' : fields.char('Telephone Personnel', size=128),
        'licexpiry' : fields.char('Lic Expiry', size=128),
        'licenseno' : fields.char('Lic No', size=128),
        'licensetyp' : fields.char('Lic Type', size=128),
    }
    _defaults = {
        'chargefam' : lambda * a: 0,
        'logement' : lambda * a: 0,
        'anciennete' : lambda * a: 'True',
        'affilie' : lambda * a: 'True',
        'date' : lambda * a: time.strftime('%Y-%m-%d'),
        'mode_reglement' : lambda * a: 'virement'
    }
hr_employee()


class hr_contract(osv.osv) :
    _inherit = 'hr.contract'
    _description = 'Employee Contract'
    _columns = {
                'working_days_per_month' : fields.integer('jours travailles par mois'),
                'hour_salary' : fields.float('salaire Heure'),
                'monthly_hour_number' : fields.float('Nombre Heures par mois'),
                'cotisation':fields.many2one('hr.payroll_ma.cotisation.type', 'Type cotisations', required=True),
                'rubrique_ids': fields.one2many('hr.payroll_ma.ligne_rubrique', 'id_contract', 'Les rubriques'),


}
    _defaults = {
        'working_days_per_month' : lambda * a : 26,
        
    }
    def net_to_brute(self, cr, uid, ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        id_contract = ids[0]
        contract = pool.get('hr.contract').browse(cr, uid, id_contract)
        salaire_base = contract.wage
        cotisation = contract.cotisation
        personnes = contract.employee_id.chargefam
        params = self.pool.get('hr.payroll_ma.parametres')
        objet_ir = self.pool.get('hr.payroll_ma.ir')
        id_ir = objet_ir.search(cr, uid, [])
        liste = objet_ir.read(cr, uid, id_ir, ['debuttranche', 'fintranche', 'taux', 'somme'])
        ids_params = params.search(cr, uid, [])
        dictionnaire = params.read(cr, uid, ids_params[0])
        abattement = personnes * dictionnaire['charge']
        base = 0
        salaire_brute = salaire_base
        trouve=False
        trouve2=False
        while(trouve == False):
            salaire_net_imposable=0
            cotisations_employee=0
            for cot in cotisation.cotisation_ids :
                if cot.plafonee and salaire_brute >= cot.plafond:
                    base = cot.plafond
                else : base = salaire_brute
                cotisations_employee += base * cot['tauxsalarial'] / 100
            fraispro = salaire_brute * dictionnaire['fraispro'] / 100
            if fraispro < dictionnaire['plafond']:
                salaire_net_imposable = salaire_brute - fraispro - cotisations_employee
            else :
                salaire_net_imposable = salaire_brute - dictionnaire['plafond'] - cotisations_employee
            for tranche in liste:
                if(salaire_net_imposable >= tranche['debuttranche']/12) and (salaire_net_imposable < tranche['fintranche']/12):
                    taux = (tranche['taux'])
                    somme = (tranche['somme']/12) 
            ir = (salaire_net_imposable  - (somme*12))*taux/100 - abattement
            if(ir < 0):ir = 0
            salaire_net=salaire_brute - cotisations_employee - ir
            if(int(salaire_net)==int(salaire_base) and trouve2==False):
                trouve2=True
                salaire_brute-=1
            if(round(salaire_net,2)==salaire_base):trouve=True
            elif trouve2==False : salaire_brute+=0.5
            elif trouve2==True : salaire_brute+=0.01
            
        self.write(cr, uid, [contract.id], {'wage' : round(salaire_brute,2)})
        return True
            
            
       
hr_contract()
class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _description = 'Holidays'
    _columns = {
        'payed':fields.boolean('paye', required=False),
    }
    _defaults = {
        'payed': lambda * args: True
    }
hr_holidays_status()

