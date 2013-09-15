from osv import fields, osv
import time


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _description = "Car Followup"

    _columns = {
        'prod_lot_id' : fields.many2one('stock.production.lot', 'Serie'),
        'carte_bleue' : fields.char('Carte Bleue',size=10),
        'valid': fields.date('Validite CB'),
        'observation': fields.char('Observation',size=128),
        'model_1':fields.boolean('Modele No1'),
        'reception_technique':fields.boolean('Rec. Tech.'),
        'attestation_vente':fields.boolean('Att. Vente'),
        'etat_immatriculation':fields.boolean('Etat Immat.'),
        'etat_carte_grise':fields.selection([('bureau1','Centre Imm.'),('bureau2','Faritany'),('recu', 'Recu')], 'Etat CG'), 
        'no_carte_grise':fields.char('No. CG',size=10),
        'date_cg': fields.date('Date CG'),    
        'etat_gage':fields.selection([('preparatif','Prep. Docs'),('demande','Faritany'),('recu', 'Recu')], 'Etat Gage'), 
        'date_gage': fields.date('Date Ins. de Gage'), 
        'levee_gage':fields.boolean('Levee Gage'),
        'radiation':fields.boolean('Recu Radiation'),
    }
account_invoice_line()
