# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from osv import fields,osv
from tools.translate import _
import decimal_precision as dp

class share_types(osv.osv):
    _name = "share.types"
    _columns = {
        'name': fields.char('Share Type', size=64),
    }
share_types()

class shareholders(osv.osv):
    _name = "shareholders"

    def _calc_balance_shares(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for line in self.browse(cr, uid, ids):
            price = line.num_shares
            price-= line.trans
            res[line.id] = price
        return res

    def _get_share_balance(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        balance = 0.0

        for line in self.browse(cr, uid, ids):
            balance += float(line.balance)
        print balance

        for line2 in self.browse(cr, uid, ids):
            perc=float(line2.balance)/balance
            res[line2.id]=perc*100
        return res

    _columns = {
      'name': fields.many2one('res.partner', 'Name'),
        'type':fields.many2one('share.types', 'Type'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'certificate_number':fields.char('Cert. #',size=64),
        'num_shares': fields.integer('Shares'),
        'trans': fields.integer('Transferred'),
        'balance': fields.function(_calc_balance_shares,type='integer',method=True,string='Balance'),
        'share_value': fields.float('Value'),
        'par_value': fields.float('Par'),
        'value': fields.float('Value'),
        'country_id': fields.many2one('res.country', 'Country'),
        'distinct_start_number': fields.integer('Start#'),
        'distinct_end_number': fields.integer('End#'),  
        'opened_date':fields.date('Acquired'),
        'modified_date':fields.date('Transfer'),
        'share_holding_perc':fields.function(_get_share_balance,type='float',method=True,string='% Held'),
        'state': fields.selection([
            ('open','Open'),
            ('transfer','Transferred'),
            ], 'Status'),
        'remarks':fields.char('Remarks',size=256),
        }

    def onchange_distinct_start_number(self, cr, uid, ids, distinct_start_number, context=None):
        return {'value': {'distinct_end_number': endnum,'certificate_number': num_shares}}

    def transfer(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'transfer','modified_date': time.strftime('%Y-%m-%d')})
		return True


    _defaults = {
        'state': 'open',
     }

shareholders()

class investments(osv.osv):
    _name = "investments"

    def _calc_balance_shares(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for line in self.browse(cr, uid, ids):
            price = line.num_shares
            price-= line.trans
            res[line.id] = price
        return res

    def _get_share_balance(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        balance = 0.0

        for line in self.browse(cr, uid, ids):
            balance += float(line.balance)
        print balance

        for line2 in self.browse(cr, uid, ids):
            perc=float(line2.balance)/balance
            res[line2.id]=perc*100
        return res

    _columns = {
        'name': fields.many2one('res.partner', 'Name'),
        'type':fields.many2one('share.types', 'Type'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'certificate_number':fields.char('Cert. #',size=64),
        'num_shares': fields.integer('Shares'),
        'trans': fields.integer('Transferred'),
        'balance': fields.function(_calc_balance_shares,type='integer',method=True,string='Balance'),
        'share_value': fields.float('Value'),
        'par_value': fields.float('Par'),
        'value': fields.float('Value'),
        'country_id': fields.many2one('res.country', 'Country'),
        'distinct_start_number': fields.integer('Start#'),
        'distinct_end_number': fields.integer('End#'),  
        'opened_date':fields.date('Acquired'),
        'modified_date':fields.date('Transfer'),
        'share_holding_perc':fields.function(_get_share_balance,type='float',method=True,string='% Held'),
        'state': fields.selection([
            ('open','Open'),
            ('transfer','Transferred'),
            ], 'Status'),
        'remarks':fields.char('Remarks',size=256),
        }

    def transfer(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'transfer','modified_date': time.strftime('%Y-%m-%d')})
		return True

    _defaults = {
        'state': 'open',
     }

investments()

class account_types(osv.osv):
    _name = "account.types"
    _columns = {
        'name': fields.char('Account Type', size=64),
    }
account_types()

class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
        'currency_id':fields.many2one('res.currency', 'Currency'),
        'type':fields.many2one('account.types', 'Type'),
        'status': fields.selection([
                ('Active','Active'),
                ('Dormant','Dormant'),
                ('Closed','Closed'),
                ('Blocked','Blocked'),
                ], 'Status'),
    }
res_partner_bank()


class signatories(osv.osv):
    _name = "signatories"

    _columns = {
        'bank_id':fields.many2one('res.partner.bank','Bank Account'),
        'partner_id':fields.many2one('res.partner','Partner'),
        'signatory':fields.many2one('res.partner','Signatory'),
        'group':fields.char('Group',size=64),
        'type2':fields.char('Type',size=64),
        'status':fields.char('Status',size=64),
        'currency' : fields.many2one('res.currency','Currency'),
        'bank' : fields.char('Bank',size=64),
        'date_opened': fields.date('Date Appointed'),
        'date_closed': fields.date('Date Resigned'),
        'mode_operation': fields.text('Mode Of Operations'),
    }

    def onchange_bank_id(self, cr, uid, ids, bank_id):

        res = {}
        if bank_id:

            bank = self.pool.get('res.partner.bank').browse(cr, uid, bank_id)
            res['currency']=bank.currency_id.id
            res['bank']=bank.bank.name
            res['type2']=bank.type.name
            res['status']=bank.status   
        return {'value':res}

signatories()

class classifications(osv.osv):
    _name = "classifications"
    _columns = {
        'id':fields.char('ID',size=64),
        'name': fields.char('Classification', size=64),
    }
classifications()

class crm_case_section(osv.osv):
    _inherit = "crm.case.section"
    _columns = {
        'name': fields.char('Team', size=64, required=True, translate=True),
    }
crm_case_section()

class fees(osv.osv):
    _name = "fees"
    _columns = {
        'name':fields.char('Invoices', size=64),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'currency' : fields.many2one('res.currency','Currency'),
        'amount':fields.float('Amount'),
        'invoice_date':fields.date('Invoice Date'),
        'paid_date': fields.date('Date Paid'),
        'notes': fields.text('Note'),
    }
    _order = 'paid_date desc'

fees()

class treaty_countries(osv.osv):
    _name = "treaty_countries"
    _columns = {
        'country':fields.many2one('res.country', 'Country'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'renewal_date': fields.date('Renewal Date'),
        'expiry_date': fields.date('Expiry Date'),
        'application_date': fields.date('Application Date'),
        'isnew': fields.boolean('New ?'),
    }
treaty_countries()

class cat_type(osv.osv):
    _name = "cat_type"
    _columns = {
        'name':fields.char('Category', size=64),
    }
cat_type()

class cats(osv.osv):
    _name = "cats"
    _auto='false'
    _columns = {
        'name':fields.many2one('cat_type', 'Category'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
cats()

class fsc_filing(osv.osv):
    _name = "fsc.filing"
    _auto='false'
    _columns = {
        'name':fields.char('Period', size=64),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'filing_date': fields.date('filing Date'),
    }
    _order='filing_date desc'
fsc_filing()

class kyc_type(osv.osv):
    _name = "kyc.type"
    _columns = {
        'name':fields.char('Type', size=64),
    }
kyc_type()

class kyc(osv.osv):
    _name = "kyc"
    _auto='false'
    _columns = {
        'name':fields.many2one('kyc.type', 'Document'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'date': fields.date('Date'),
      'expiry': fields.date('Expiry'),
      'status': fields.selection([
            ('submitted','Submitted'),
            ('missing','Missing'),
        ('incorrect','Incorrect'),
        ('exempted','Exempted'),
            ], 'Status'),

    }
kyc()

class secretary_months(osv.osv):
    _name = "secretary.months"
    _columns = {
        'name':fields.char('Month', size=64),
    }
secretary_months()

class aps_quarter(osv.osv):
    _name = "aps.quarter"
    _columns = {
        'name':fields.char('Quarter', size=64),
    }
aps_quarter()

class aps(osv.osv):
    _name = "aps"
    _auto='false'
    _columns = {
        'name':fields.char('Quarter', size=64),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'start_period': fields.many2one('secretary.months', 'Start'),
        'end_period': fields.many2one('secretary.months', 'End'),
        'due_date': fields.many2one('secretary.months', 'Due Date'),
    }
aps()

class bills(osv.osv):
    _name = "bills"
    _auto='false'
    _columns = {
        'name':fields.many2one('aps.quarter', 'Quarter'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'start_period': fields.many2one('secretary.months', 'Start'),
        'end_period': fields.many2one('secretary.months', 'End'),
        'due_date': fields.many2one('secretary.months', 'Due Date'),
    }
aps()

class partner_status(osv.osv):
    _name = "partner.status"
    _auto='false'
    _columns = {
        'name':fields.char('Status', size=64),
    }
partner_status()

class type_type(osv.osv):
    _name = "type_type"
    _columns = {
        'name':fields.char('Type', size=64),
    }
type_type()

class types(osv.osv):
    _name = "types"
    _auto='false'
    _columns = {
        'name':fields.many2one('type_type', 'Type'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
types()

class nature_type(osv.osv):
    _name = "nature_type"
    _columns = {
        'name':fields.char('Nature', size=64),
    }
nature_type()

class natures(osv.osv):
    _name = "natures"
    _auto= 'false'
    _columns = {
        'name':fields.many2one('nature_type', 'Nature'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
natures()

class turnovers(osv.osv):
    _name = "turnovers"
    _auto= 'false'
    _columns = {
        'amount':fields.float('Amount'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'record_date': fields.date('Date Recorded'),
    }
    _order='record_date desc'
turnovers()

class names(osv.osv):
    _name = "names"
    _auto= 'false'
    _columns = {
        'name':fields.char('Name', size=64),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
names()

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _columns = {
        'type': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Registered'), ('other','Other') ],'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),
        'effective_date':fields.date('Effective Date'),
    }
    _order='type,effective_date desc'
    _defaults = {
        'type': 'contact',
    }
res_partner_address()

class ownership(osv.osv):
    _name = "ownership"
    _columns = {
        'name': fields.many2one('res.partner', 'Name'),
        'date':fields.date('Start'),
        'date_end':fields.date('End'),
        'description':fields.char('Description',size=128),
        'type':fields.selection([
            ('nominee','Nominee'),
            ('owner','Beneficial Owner'),
            ], 'Type'),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'share_holding_perc':fields.float('% Held'),
        }

ownership()

class acct_year_end(osv.osv):
    _name = "acct.year.end"
    _columns = {
      'name': fields.many2one('secretary.months', 'Name'),
      'partner_id':fields.many2one('res.partner', 'Partner'),
        }

acct_year_end()


class res_partner(osv.osv):

    _inherit = "res.partner"
    _table = "res_partner"
    _auto = True

    _columns = {
        'seal_number':fields.char('Seal Number', size=64),
        'isclient': fields.boolean('Client ?'),
        'dob': fields.date('Date of Birth/Regn.'),
        'title':fields.many2one('res.partner.title', 'Title'),
        'id_number': fields.char('File/ID Number', size=64),
        'ref_no': fields.char('Ref. Number', size=64),
        'licence_number': fields.char('Licence Number', size=64),
        'paye': fields.char('PAYE Number', size=64),
        'npf': fields.char('NPF Number', size=64),  
        'tan': fields.char('Tax Account Number', size=64),
        'brn': fields.char('Business Reg. Number', size=64),
        'classification': fields.many2one('classifications','Classification'),
        'risk': fields.selection([('low', 'Low'),
                                        ('medium', 'Medium'),
                                        ('high', 'High'),
                                        ('default_low', 'Default Low')], 'Risk Scale',),
       'licence_date': fields.date('Licence Date'),
       'date_agm': fields.date('AGM Date'),
       'relation_ids':fields.one2many('relations','partner_id','Relations'),
       'shareholder_ids':fields.one2many('shareholders', 'partner_id','Shareholders'),
       'investment_ids':fields.one2many('investments', 'partner_id','Investments'),
       'ownership_ids':fields.one2many('ownership', 'partner_id','Ownership'),
       'lic_expiry': fields.date('Licence Exp.'),
       'trc_renewal': fields.date('TRC Renewal Date'),
       'treaty_ids':fields.one2many('treaty_countries', 'partner_id','Treaty Countries'),
       'contract_ids':fields.one2many('contracts', 'partner_id','Contracts'),
       'signatory_ids':fields.one2many('signatories', 'partner_id','Signatories'),
       'fees_ids':fields.one2many('fees', 'partner_id','Fees'),
       'referral':fields.many2one('res.partner','Introducer'),
       'currency_id' : fields.many2one('res.currency','Currency'),
       'entity_ids': fields.one2many('entities','partner_id','Entity'),
       'cat_ids': fields.one2many('cats','partner_id','Entity'),
       'fsc_filing_ids': fields.one2many('fsc.filing','partner_id','FSC Filing'),
       'type_ids': fields.one2many('types','partner_id','Entity'),
       'nature_ids': fields.one2many('natures','partner_id','Entity'),
       'turnover_ids': fields.one2many('turnovers','partner_id','Turnover'),
       'lob_ids': fields.one2many('lobs','partner_id','Entity'),
       'accounting_year_end': fields.many2one('secretary.months','Accounting Year End'),
       'name_ids': fields.one2many('names','partner_id','Names'),
       'current_cat': fields.related('cat_ids', 'name', type='many2one', relation='cat_type', string='Category', readonly=True),
       'current_entity': fields.related('entity_ids', 'type', type='many2one', relation='entity.type', string='Entity', readonly=True),
       'current_nature': fields.related('nature_ids', 'name', type='many2one', relation='nature_type', string='Nature', readonly=True),
       'current_turnover': fields.related('turnover_ids', 'amount', type='many2one', relation='amount', string='Turnover', readonly=True),
       'current_lob' : fields.related ('lob_ids','name',type='char',string='Business', readonly=True),
       'last_fsc_filing' : fields.related ('fsc_filing_ids','filing_date',type='date',string='Last FSC Filing', readonly=True),
       'kyc_ids': fields.one2many('kyc','partner_id','KYC'),
       'aps_ids': fields.one2many('aps','partner_id','APS'),
       'status': fields.many2one('partner.status','Status'), 
       'reminder_ids': fields.one2many('res.reminder','partner_id','Reminders'),
          }
    def create_aps(self, cr, uid, ids, month,context='None'):
        months=self.pool.get('secretary.months')
        for x in self.browse(cr, uid, ids):
            month=x.accounting_year_end.id

        aps=self.pool.get('aps')
        for line in months.browse(cr,uid,ids):
            partner=line.id

        start_period=month+1
        if start_period>12:
            start_period=start_period-12
        
        end_period=start_period+2
        if end_period>12:
            end_period=end_period-12

        due_date=end_period+3        
        if due_date>12:
            due_date=due_date-12

        aps.create(cr,uid,{'name':'First','partner_id':partner,'start_period':start_period,'end_period':end_period,'due_date':due_date})
        
        start_period=end_period+1
        if start_period>12:
            start_period=start_period-12
        
        end_period=start_period+2
        if end_period>12:
            end_period=end_period-12

        due_date=end_period+3        
        if due_date>12:
            due_date=due_date-12        
                
        
        aps.create(cr,uid,{'name':'Second','partner_id':partner,'start_period':start_period,'end_period':end_period,'due_date':due_date})
        
        start_period=end_period+1
        if start_period>12:
            start_period=start_period-12
        
        end_period=start_period+2
        if end_period>12:
            end_period=end_period-12

        due_date=end_period+3        
        if due_date>12:
            due_date=due_date-12      
        
        aps.create(cr,uid,{'name':'Third','partner_id':partner,'start_period':start_period,'end_period':end_period,'due_date':due_date})

        start_period=month+1
        if start_period>12:
            start_period=start_period-12
        
        end_period=month
        if end_period>12:
            end_period=end_period-12

        due_date=month+6        
        if due_date>12:
            due_date=due_date-12      

        aps.create(cr,uid,{'name':'Final','partner_id':partner,'start_period':start_period,'end_period':end_period,'due_date':due_date})
        return False

res_partner()


class contracts(osv.osv):
    _name = "contracts"
    _columns = {
        'name':fields.char('Contract', size=64),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'approved_date': fields.date('Date Approved'),
        'tc': fields.text('Terms & conditions'),
    }
contracts()

class entity_type(osv.osv):
    _name = "entity.type"
    _columns = {
        'name': fields.char('Entity Type', size=64),
    }
entity_type()

class entities(osv.osv):
    _name = "entities"
    _columns = {
        'id': fields.char('ID', size=64),
        'type':fields.many2one('entity.type', 'Entity'),
        'partner_id': fields.many2one('res.partner', 'Parent'),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
entities()


class lobs(osv.osv):
    _name = "lobs"
    _auto= 'false'
    _columns = {
        'name':fields.char('Line Of Business', size=64),
        'partner_id':fields.many2one('res.partner', 'Parent'),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
lobs()

class relation_type(osv.osv):
    _name = "relation.type"
    _columns = {
        'name': fields.char('Relation Type', size=64),
    }
relation_type()

class relations(osv.osv):
    _name = "relations"
    _auto= "false"
    _columns = {
        'id': fields.char('ID', size=64),
        'type':fields.many2one('relation.type', 'Type'),
        'partner_id': fields.many2one('res.partner', 'Parent'),
        'relative': fields.many2one('res.partner', 'Name'),
        'status': fields.selection([('active', 'Active'),
                                    ('resigned', 'Resigned')], 'Status',),
        'appoint_date': fields.date('Date Appointed'),
        'resign_date': fields.date('Date Resigned'),
    }
    _order='resign_date desc'
    _defaults = {

    }
relations()


class payment_modes(osv.osv):
    _name = "payment.modes"
    _columns = {
        'name': fields.char('Payment Mode', size=64),
    }
payment_modes()

class res_director(osv.osv):
    _name = "res.director"
    _columns = {
        'id': fields.char('ID', size=64),
        'name': fields.char('Partner Name', size=64),
        'status': fields.selection([('active', 'Active'),
                                    ('resigned', 'Resigned')], 'Status',),
        'date_appointed': fields.date('Date Appointed'),
        'date_resigned': fields.date('Date Resigned'),
    }
res_director()


class tax_residence_certificates(osv.osv):
    _name = "tax.residence.certificates"
    _columns = {
        'country_id': fields.many2one('res.country', 'Country'),
        'application_date': fields.date('Application Date'),
        'renewal_date': fields.date('Expiry Date'),
        'expiry_date': fields.date('Expiry Date'),
        'isnew': fields.boolean('New ?'),
    }
tax_residence_certificates()

class roc_fees(osv.osv):
    _name = "roc.fees"
    _columns = {
        'payment_date': fields.date('Payment Date'),
        'amount': fields.float('Amount'),
    }
roc_fees()

class fsc_fees(osv.osv):
    _name = "fsc.fees"
    _columns = {
        'payment_date': fields.date('Payment Date'),
        'amount': fields.float('Amount'),
    }
fsc_fees()

class issue_share(osv.osv):
    _name = "issue.share"
    _columns = {
        'issure_id': fields.many2one('res.partner','Issure'),
        'share_type': fields.selection([('ordinary', 'Ordinary'),
                                    ('preferential', 'Preferential')], 'Share Type',),
        'number_share': fields.float('Number of shares'),
        'value': fields.float('Value'),
        'series': fields.char('Series', size=64),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
issue_share()

class transfer_share(osv.osv):
    _name = "transfer.share"
    _columns = {
        'certificate': fields.char('Share Certificate Number',size=64),
        'transfer_to': fields.many2one('res.partner','Transfer To'),
        'share_type': fields.selection([('ordinary', 'Ordinary'),
                                    ('preferential', 'Preferential')], 'Share Type',),
        'number_share': fields.float('Number of shares'),
        'value': fields.float('Value'),
        'series': fields.char('Series', size=64),
        'effective_date': fields.date('Effective Date'),
    }
    _order='effective_date desc'
transfer_share()

class res_meeting(osv.osv):
    _name = "res.meeting"
    _columns = {
        'venue': fields.char('Venue',size=64),
        'type': fields.selection([('agm', 'AGM'),
                                    ('special', 'Special'),
                                    ('shareholders', 'Share Holders'),
                                    ('board', 'Board')], 'Type'),
        'date1': fields.date('Date And Time'),
    }
res_meeting()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
