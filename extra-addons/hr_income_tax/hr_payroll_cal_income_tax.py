from osv import fields, osv
import decimal_precision as dp
import tools
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import datetime
import time
import calendar
import pooler


class cal_allowance_tax(osv.osv):
    _name ='cal.allowance.tax'
    _description='CALCULATION OF ALLOWANCE'
    _rec_name = 'final_exemption_amt'
    
    
    def _basic_hra_amt(self, cr, uid, ids, name, args, context=None):
        res = {}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                    for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'BASIC':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res

    def _hra_amt(self, cr, uid, ids, name, args, context=None):
        res = {}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                    hra_amt = 0.0
                    for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'HRA':
                            hra_amt += s_obj_l.total
                            break
                res[d_obj.id]= hra_amt
        return res
    
    def _total_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                res[d_obj.id]= len(d_obj.emp_id.slip_ids)
        return res
    
    def _exemption_amt(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            b_sal=0.00
            for s_obj in obj.emp_id.slip_ids:
                for s_obj_l in s_obj.line_ids:
                    if s_obj_l.code == 'BASIC':
                        b_sal += s_obj_l.total
                        break
            localdict = {'basic_hra':obj.basic_hra, 'ded_pec1':(obj.ded_pec1)*0.01, 'hra_rec':obj.hra_rec, 'rent_paid_hra':obj.rent_paid_hra, 'ded_pec2':(obj.ded_pec2)*0.01, 'basic':b_sal  }
            exec obj.python_compute in localdict
            res[obj.id] = localdict['result']
        return res  
    
    def _con_all_allowance(self, cr, uid, ids, name, args, context=None):
        res = {}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                    for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'CA':
                            result += s_obj_l.total
                            break
                    total_month = len(d_obj.emp_id.slip_ids)
                    localdict = { 'con_all_hra' : result, 'count_month':  total_month, 'phy_handicap':  ''}
                    exec d_obj.python_compute_cov in localdict
                    res[d_obj.id] = localdict['result_Conv_all']
        return res


    def _pt(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'PT':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res
    
    def _med_reimbersement(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'MR':
                            result += s_obj_l.total
                            break
                localdict = { 'MR' : result }
                exec d_obj.python_compute_mr in localdict
                res[d_obj.id] = localdict['result_mr']
        return res

    def _lta(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'LTA':
                            result += s_obj_l.total
                            break
                localdict = { 'LTA' : result , 'lta_paid': d_obj.lta_paid }
                exec d_obj.python_compute_lta in localdict
                res[d_obj.id] = localdict['result_lta']
        return res

    def _le(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'LE':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res

    def _vma(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'VMA':
                            result += s_obj_l.total
                            break
                total_month = len(d_obj.emp_id.slip_ids)
                localdict = { 'VMA' : result , 'driver_allot': '' ,'cc': '', 'month':  total_month }
                exec d_obj.python_compute_vma in localdict
                res[d_obj.id] = localdict['result_vma']
        return res
    
    def _ea(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'EA':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res

    def _aa(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'AA':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res

    def _ua(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'UA':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res

    def _eda(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'EDA':
                            result += s_obj_l.total
                            break
                localdict = { 'EDA' : result , 'Nochield':  False }
                exec d_obj.python_compute_eda in localdict
                res[d_obj.id] = localdict['result_eda']
        return res

    def _ha(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'HA':
                            result += s_obj_l.total
                            break
                localdict = { 'HA' : result , 'Nochield':  d_obj.emp_id.children }
                exec d_obj.python_compute_ha in localdict
                res[d_obj.id] = localdict['result_ha']
        return res

    def _na(self, cr, uid, ids, name, args, context=None):
        res ={}
        data_obj =  self.browse(cr,uid,ids,context)
        if data_obj:
            for d_obj in data_obj:
                result = 0.00
                for s_obj in d_obj.emp_id.slip_ids:
                   for s_obj_l in s_obj.line_ids:
                        if s_obj_l.code == 'NA':
                            result += s_obj_l.total
                            break
                res[d_obj.id] = result
        return res

    def _final_exemption_amt(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            res[obj.id] = {
                'final_exemption_amt': 0.0
            }
            res[obj.id]['final_exemption_amt']= (obj.exemption_amt + obj.con_all_hra + obj.professional_tax 
                                                 + obj.med_reimbersement + obj.lta 
                                                 + obj.le + obj.vma + obj.ea 
                                                 + obj.aa + obj.ua + obj.eda
                                                 + obj.ha + obj.na)
        return res
    
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'it_id':fields.one2many('cal.income.tax', 'less', 'Tax Lines'),
                'rent_paid_hra':fields.float('Rent Paid', digits_compute=dp.get_precision('Payroll')),
                'count_month':fields.function(_total_month, string='Month', method=True, store=True, type='integer'),
                'basic_hra':fields.function(_basic_hra_amt, method=True, digits_compute=dp.get_precision('Payroll'), string='Basic Sal (Basic+DA)', store=True),
                'hra_rec':fields.function(_hra_amt, method=True, digits_compute=dp.get_precision('Payroll'), string='H.R.A Received',store=True),
                'ded_pec1':fields.float('Maximum Amt (In %)', digits_compute=dp.get_precision('Payroll')),
                'ded_pec2':fields.float('Calculated Basic Salary (In %)', digits_compute=dp.get_precision('Payroll')),
                'python_compute':fields.text('Python Code'),
                'exemption_amt':fields.function(_exemption_amt, method=True, digits_compute=dp.get_precision('Payroll'), string='Exemption Amount',store=True),
                'python_compute_cov':fields.text('Python Code'),
                'con_all_hra':fields.function(_con_all_allowance, method=True, digits_compute=dp.get_precision('Payroll'), string='Conveyance Allowances',
                      store=True,help='Conveyance allowances(Max Rs.800/-p.m)'),
                'professional_tax':fields.function(_pt, method=True, digits_compute=dp.get_precision('Payroll'), string='Professional Tax',store=True),
                'med_reimbersement':fields.function(_med_reimbersement, method=True, digits_compute=dp.get_precision('Payroll'),string='Medical Reimbersement',store=True),
                'python_compute_mr':fields.text('Python Code'),
                'lta_paid':fields.float('LTA Paid', digits_compute=dp.get_precision('Payroll')),
                'lta':fields.function(_lta, method=True, digits_compute=dp.get_precision('Payroll'),string='L.T.A.(as per rule)',store=True),
                'python_compute_lta':fields.text('Python Code'),
                'le':fields.function(_le, method=True, digits_compute=dp.get_precision('Payroll'),string='Leave (Encashment/Salary)',store=True),
                'vma':fields.function(_vma, method=True, digits_compute=dp.get_precision('Payroll'),string='Vehicle Maintenance Allowance',store=True),
                'python_compute_vma':fields.text('Python Code'),
                'ea':fields.function(_ea, method=True, digits_compute=dp.get_precision('Payroll'),string='Entertaintment Allowance',store=True),
                'aa':fields.function(_aa, method=True, digits_compute=dp.get_precision('Payroll'),string='Academic Allowance',store=True),
                'ua':fields.function(_ua, method=True, digits_compute=dp.get_precision('Payroll'),string='Uniform Allowances',store=True),
                'eda':fields.function(_eda, method=True, digits_compute=dp.get_precision('Payroll'),string='Education Allowance',store=True),
                'python_compute_eda':fields.text('Python Code'),
                'ha':fields.function(_ha, method=True, digits_compute=dp.get_precision('Payroll'),string='Hostel Allowance',store=True),
                'python_compute_ha':fields.text('Python Code'),
                'na':fields.function(_na, method=True, digits_compute=dp.get_precision('Payroll'),string='Newspaper Allowance',store=True),
                'final_exemption_amt':fields.function(_final_exemption_amt, method=True, digits_compute=dp.get_precision('Payroll'),string='Final Exemption Amount', 
                     store={
                            'cal.allowance.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                            },
                    multi='all'),              
                }
    _defaults = {
                  'python_compute': lambda *a: '''#HRA Exemption\n#Exemption Amount : cal.allowance.tax object\n\nresult = abs(min(( basic_hra * ded_pec1),hra_rec,(rent_paid_hra - (ded_pec2 * basic)) > 0.0 and (rent_paid_hra - (ded_pec2 * basic)) or 0.0)) ''',
                  'python_compute_cov': lambda *a: '''#Conveyance Allowances\n#Conveyance Allowances : cal.allowance.tax object\n\nresult_Conv_all = (phy_handicap and min(con_all_hra,(1600 * count_month)) or min(con_all_hra,(800 * count_month))) ''',
                  'python_compute_mr': lambda *a: '''#Medical Reimbersement Allowances\n#Medical Reimbersement : cal.allowance.tax object\n\nresult_mr = min(MR,15000) ''',
                  'python_compute_lta': lambda *a: '''#L.T.A. Allowances\n#L.T.A. : cal.allowance.tax object\n\nresult_lta = min(LTA,lta_paid) ''',
                  'python_compute_vma': lambda *a: '''#Vehicle Maintenance Allowance\n#Vehicle Maintenance Allowance : cal.allowance.tax object\n\nresult_vma = min(VMA,(driver_allot and ((cc < 1600 and 1200 or 1600) + 600) or (cc < 1600 and 1200 or 1600))*month ) ''',
                  'python_compute_eda': lambda *a: '''#Education Allowance\n#Education Allowance : cal.allowance.tax object\n\nresult_eda = min((min(Nochield,2)*100),EDA) ''',
                  'python_compute_ha': lambda *a: '''#Hostel Allowance\n#Hostel Allowance : cal.allowance.tax object\n\nresult_ha = min((min(Nochield,2)*300),HA) ''',
                  'ded_pec1': lambda *a: 40.0,
                  'ded_pec2': lambda *a: 10.00,
                 }
    
cal_allowance_tax()

class cal_other_income_tax(osv.osv):
    _name ='cal.other.income.tax'
    _description='CALCULATION OF OTHER INCOME'
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'name': fields.char('Other Name', size=64,required=True),
                'amt' : fields.float('Any Other Income',help='Any Other Income (specify)',required=True),
              }
cal_other_income_tax()

class cal_interest_received_tax(osv.osv):
    _name ='cal.interest.received.tax'
    _description='CALCULATION OF INTEREST RECEIVED'
    _rec_name='other_total'
    
    def _other_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        other_result_amt=0.00
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            for other in obj.other_income:
                other_result_amt += other.amt
            res[obj.id]= (obj.bank + obj.nsc + obj.mis
                        + obj.post_off_recuring + obj.term_dep 
                        + obj.saving + obj.kishan + other_result_amt)
        return res
    
    
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'it_id':fields.one2many('cal.income.tax','name','Tax Declaration'),
                'bank' : fields.float('Bank',help='Bank( Saving /FD /Rec )'),
                'nsc' : fields.float('N.S.C.',help='N.S.C.(accrued/ Recd )'),
                'mis':fields.float('Post Ofice M.I.S ',help='Post Ofice M.I.S (6 yrs.)'),
                'post_off_recuring':fields.float('Post Office Recring Deposit',help='Post Office Recring Deposit (5 yrs.)'),
                'term_dep' : fields.float('Term Deposit',help='Term Deposit (1 to 5 yrs.)'),
                'saving' : fields.float('Saving Bonds',help='Saving Bonds (6yrs.)'),
                'kishan' : fields.float('Kishan Vikas patra'),
                'other_income':fields.many2many('cal.other.income.tax','other_d','cal_r_id' ,'cal_other_id','Other Income Detail'),
                'other_total': fields.function(_other_total, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Other Income',store=True),              
              }
cal_interest_received_tax()

class cal_house_property(osv.osv):
    _name ='cal.house.property'
    _description='CALCULATION OF HOUSE PROPERTY'

    def onchange_type(self, cr, uid, ids,type,av,mt,nav,r_c_charges,i_h_loan):
        res = {}
        if not type:
            return {'value' : {}}
        if type == 'self_occupied':
            res['av']=0.00
            res['mt']=0.00
            if ids:
                self.write(cr,uid,ids,res)
        else:
            res['type'] = type
            res['av']=av
            res['mt']=mt
            res['nav']=nav
            res['r_c_charges']=r_c_charges
            res['i_h_loan']=i_h_loan
        return {
            'value' : res
    }
                
    def _nav(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            if obj.type == 'self_occupied':
                res[obj.id] = 0.0
            else:
                res[obj.id]= obj.av - obj.mt
        return res

    def _rcc(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            if obj.type == 'self_occupied':
                res[obj.id] = 0.0
            else:
                res[obj.id]= obj.nav * 0.30
        return res

    def _ihl(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            type = False
            if obj.type == 'self_occupied':
                type = True
            localdict = { 'type' : type , 'date':  obj.loan_date,'loan_amt': obj.loan_amt  }
            exec obj.python_compute_ihl in localdict
            res[obj.id] = localdict['result_ihl']
        return res

    def _tna(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids)
        for obj in obj_l:
            res[obj.id] = {
                           'total_net_amt':0.00
                           }
         
            res[obj.id]['total_net_amt'] = obj.nav - (obj.r_c_charges + obj.i_h_loan)
        return res
   
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'it_id':fields.one2many('cal.income.tax','name','Tax Declaration'),
                'name': fields.char('House Name', size=64,required=True),
                'type' : fields.selection([('let_out_property','Let Out Property'),('self_occupied','Self Occupied')], 'Type',required=True),
                'loan_date':fields.date('Loan Taken Date',required=True),
                'loan_amt':fields.float('Laon Amount'),
                'av' : fields.float('Annual Value',help='Annual Value for let out house property'),
                'mt' : fields.float('Municipal Taxes',help='Municipal Taxes paid by landlord on letout house property'),
                'nav' : fields.function(_nav, method=True, digits_compute=dp.get_precision('Payroll'),string='Net Annual Value',store=True),
                'r_c_charges' : fields.function(_rcc, method=True, digits_compute=dp.get_precision('Payroll'),string='Repair & Collection Charges',store=True),
                'i_h_loan' : fields.function(_ihl, method=True, digits_compute=dp.get_precision('Payroll'),string='Interest On Housing Loan',store=True),              
                'python_compute_ihl':fields.text('Python Code'),
                'total_net_amt': fields.function(_tna, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Net Amount',
                     store={
                            'cal.house.property': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                            },
                    multi='all'),              
          
              }
    _defaults = {
        'type': lambda *a: 'let_out_property',
        'loan_date': lambda *a: time.strftime("%Y-%m-%d"),
        'python_compute_ihl': lambda *a: '''#Calculation of House Property\n#Income From House Property : cal.house.property object\n\nresult_ihl = (type and (date < '1999-04-01' and min(loan_amt,30000) or min(loan_amt,150000)) or loan_amt) ''',
    }
    
cal_house_property()


class cal_other_deduction_tax(osv.osv):
    _name ='cal.other.deduction.tax'
    _description='CALCULATION OF OTHER DEDECTION'
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'name': fields.char('Other Name', size=64,required=True),
                'amt' : fields.float('Any Other Deduction',help='Any Other Deduction (specify)',required=True),
              }
cal_other_deduction_tax()

class cal_deduction_tax(osv.osv):
    _name ='cal.deduction.tax'
    _description='CALCULATION OF DEDUCTION UNDER 80C'
    _rec_name='total_ded'

    def _ded_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        other_result_amt=0.00
        obj_l = self.browse(cr,uid,ids,context)
        for obj in obj_l:
            for other in obj.other_ded:
                other_result_amt += other.amt
            res[obj.id]= (obj.pf_vpf + obj.lif + obj.ppf
                          + obj.nsc1 + obj.house_loan + obj.tut_fees
                          + obj.elss + obj.tax_sav_bond + obj.fd
                          +obj.pension_plan + other_result_amt)
        return res
    
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'pf_vpf' : fields.float('PF&VPF Contribution'),
                'lif' : fields.float('Life Insurance premiums'),
                'ppf' : fields.float('PPF a/c Contribution'),
                'nsc1' : fields.float('N.S.C',help='N.S.C (Investment +accrued Int first five year)'),
                'house_loan' : fields.float('Housing. Loan',help='Housing. Loan (Principal Repayment )'),
                'tut_fees' : fields.float('Tuition  fees  for 2 children'),
                'elss' : fields.float('E.L.S.S',help='E.L.S.S(Mutual Fund)'),
                'tax_sav_bond' : fields.float('Tax Savings Bonds'),
                'fd' : fields.float('FD ',help='FD (5 Years and above)'),
                'pension_plan' : fields.float('80 ccc Pension  Plan'),
                'other_ded':fields.many2many('cal.other.deduction.tax','other_ded','cal_rd_id' ,'cal_other_ded_id','Other Deduction Detail'),
                'total_ded' : fields.function(_ded_total, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Deduction',store=True),
              }
cal_deduction_tax()


class cal_other_deduction6a_tax(osv.osv):
    _name ='cal.other.deduction6a.tax'
    _description='CALCULATION OF OTHER DEDECTION-6A'
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'name': fields.char('Other Name', size=64,required=True),
                'amt' : fields.float('Any Other Deduction-6a',help='Any Other Deduction-6a (specify)',required=True),
              }
cal_other_deduction6a_tax()

class cal_deduction_6_a_tax(osv.osv):
    _name ='cal.deduction.6.a.tax'
    _description='CALCULATION OF DEDUCTION UNDER 6-A'
    _rec_name='total_ded1'
     
    def _ded_total1(self, cr, uid, ids, name, args, context=None):
        res = {}
        other_result_amt = 0.00
        obj_l = self.browse(cr,uid,ids,context)
        for obj in obj_l:
            for other in obj.other_ded6a:
                other_result_amt += other.amt
            res[obj.id]= (obj.mip + obj.mipp + obj.int_paid_edu
                          + obj.donation_app + other_result_amt)
        return res
    
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'mip' : fields.float('Medical Insurance premiums (for Self )'),
                'mipp' : fields.float('Medical Insurance premiums (for Parents))'),
                'int_paid_edu' : fields.float('Int Paid on Education Loan'),
                'donation_app' : fields.float('Donation to approved fund'),
                'other_ded6a':fields.many2many('cal.other.deduction6a.tax','other_ded6a','cal_rd6a_id' ,'cal_other_ded6a_id','Any other (Specify)'),
                'total_ded1' : fields.function(_ded_total1, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Deduction',store=True),
              }
cal_deduction_6_a_tax()


class income_tax_rule(osv.osv):
    _name ='income.tax.rule'
    _description='INCOME TAX RULE'
    _rec_name='rule'

    def _def_rule(self, cr, uid, ids, name, args, context=None):
        res = {}
        rule = ''
        obj_l = self.browse(cr,uid,ids,context)
        for obj in obj_l:
            if obj.l_cat:
                rule_header = '''#Applied Income Tax Rule\n\n\nNet Income Range                                              Income Tax Rates\n\n--------------------------------------------------------------------------------------\nUpto Rs'''+str(obj.fully_exampt_amt or 0.00)+'''                                                NIL\n'''
                rule_body = ''
                for body_line in obj.l_cat:
                    rule_body +=str(body_line.name or '')+'  '+'Upto Rs '+str(body_line.st_amt or 0.00)+' to Rs '+str(body_line.end_amt or str(0.00)+'        ')+'                '+str(body_line.perc or 0.0)+' of Total Income(-)Rs.'+str(body_line.st_amt or 0.00)+'\n'
                rule =rule_header + rule_body
                res[obj.id]= rule
        return res
    
    _columns={
                'gender': fields.selection([('male','Male'),('female','Female')], 'Gender',required=True),
                'fully_exampt_amt' : fields.float('Fully Exampted Amount',required=True),
                'l_cat':fields.one2many('level.category','it_rule','Level Assignment'),
                'rule' : fields.function(_def_rule, type='text', method=True, string='Rule String'),
              }
    
    _defaults = {
        'gender': lambda *a: 'male',
        'fully_exampt_amt': lambda *a: 180000.00,
    }
  
income_tax_rule()

class level_category(osv.osv):
    _name ='level.category'
    _description='Level Category'

    _columns={
                'it_rule':fields.many2one('income.tax.rule','Rule'),
                'seq_no':fields.integer('Sequence',size=16,required=True),
                'name' : fields.char('Level Name', size=64,required=True),
                'st_amt' : fields.float('Start Range Amount',required=True),
                'end_amt' : fields.float('Last Range Amount'),
                'perc' : fields.float('Ralated Percent'),
              }

level_category()

class income_tax_surcharge(osv.osv):
    _name ='income.tax.surcharge'
    _description='Total Surcharge'
    _rec_name = 'sur_amt'
    _columns={
                'emp_id':fields.many2one('hr.employee','Employee',required=True),
                'sur_amt' : fields.float('Surcharge Limit Amt',required=True),
                'perc' : fields.float('Surcharge Perc(%)'),
              }
    _defaults={
              'sur_amt' : lambda *a: 1000000.00,
              'perc': lambda *a: 10,
              }
income_tax_surcharge()

class cal_income_tax(osv.osv):
    _name ='cal.income.tax'
    _description='CALCULATION OF INCOME TAX'
    
    def onchange_emp_id(self, cr, uid, ids, name):
        val={}
        if name:
            res = self.pool.get('hr.employee').read(cr, uid, [ name ],['birthday','gender','pan','esi','pf'])
            val['dob'] = res[0]['birthday']
            val['gender']=res[0]['gender']
            val['pan_no']=res[0]['pan']
            val['esi']=res[0]['esi']
            val['pf']=res[0]['pf']
        return {'value': val}

    def _all_cal(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_l = self.browse(cr,uid,ids,context)
        for obj in obj_l:
            res[obj.id] = { 'basic':0.00,'gross_salary':0.00,'gross_salary_approx':0.00,
                           'income_head_salary':0.00,'income_head_salary_approx':0.00,'income_other':0.00,
                            'income_other_approx':0.00,'gross_tol_inc':0.00,'gross_tol_inc_approx':0.00,'tot_income_':0.00,
                            'tot_income_approx':0.00,'tot_tax_inc':0.00,'tot_tax_inc_approx':0.00,'tax_on_tol':0.00,'tax_on_tol_approx':0.00,
                            'tol_tax_pay':0.00,'tol_tax_pay_approx':0.00,'add_edn_cess':0.00,'add_edn_cess_approx':0.00,
                            'net_tax_pay':0.00,'net_tax_pay_approx':0.00,'balance_tax':0.00,'balance_tax_approx':0.00}
            total_basic=0.00
            total_gross=0.00
            total_gross_approx=0.00
            for sal_obj in obj.employee.slip_ids:
                for s_obj_l in sal_obj.line_ids:
                    if s_obj_l.code == 'BASIC':
                        total_basic += s_obj_l.total
                    elif s_obj_l.code == 'GROSS':
                        total_gross += s_obj_l.total
                    else:
                        continue
            year_start_date = obj.year_detail.date_start
            year_end_date = obj.year_detail.date_stop
            contract_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',obj.employee.id),('date_start','>=',year_start_date),('date_start','<=',year_end_date)])
            if contract_ids:
                contract_objs = self.pool.get('hr.contract').browse(cr,uid,contract_ids)
                num_of_month = 0
                for cobj in contract_objs:
                    total = 0.00
                    flg = False
                    end_d = cobj.date_end
                    if not end_d:
                        end_d = year_end_date
                        flg=True
                    else:
                        if end_d >= year_start_date and end_d <= year_end_date:
                            flg=True
                    if flg:
                        tot_basic = cobj.wage
                        diff_days = (mx.DateTime.strptime(end_d, '%Y-%m-%d') - mx.DateTime.strptime(cobj.date_start, '%Y-%m-%d')).strftime('%d')
                        num_month = round(int(diff_days)/30)
                        for rule in cobj.struct_id.rule_ids:
                            if rule.category_id.name == 'Allowance':
                                if rule.amount_select == 'percentage':
                                    total+=float((tot_basic*num_month) * (rule.amount_percentage/100))
                                elif rule.amount_select == 'code':
                                    total+=(rule.amount_percentage_base*num_month)
                                else:
                                    total+=rule.amount_fix*num_month
                        total_gross_approx += round((tot_basic*num_month) + total)
            res[obj.id]['gross_salary_approx'] = total_gross_approx
            res[obj.id]['basic']= total_basic
            res[obj.id]['gross_salary']= total_gross
            res[obj.id]['income_head_salary']= total_gross - (obj.less and float(obj.less.final_exemption_amt) or 0.00)
            res[obj.id]['income_head_salary_approx']= total_gross_approx - (obj.less and float(obj.less.final_exemption_amt) or 0.00)
            res[obj.id]['income_other']= res[obj.id]['income_head_salary'] + (obj.add_any_other_income and float(obj.add_any_other_income.other_total) or 0.00)
            res[obj.id]['income_other_approx']= res[obj.id]['income_head_salary_approx'] + (obj.add_any_other_income and float(obj.add_any_other_income.other_total) or 0.00)
            total_house_amt=0.00
            for obj_h in obj.inc_h_pro:
                total_house_amt += obj_h.total_net_amt
                if total_house_amt < 0.0:
                    total_house_amt = 0.0
            res[obj.id]['gross_tol_inc']= res[obj.id]['income_other'] + total_house_amt
            res[obj.id]['gross_tol_inc_approx']= res[obj.id]['income_other_approx'] - total_house_amt
            res[obj.id]['tot_income_']= res[obj.id]['gross_tol_inc'] - (obj.dec_und_sec and obj.dec_und_sec.total_ded or 0.00 + obj.ded_under_chp and obj.ded_under_chp.total_ded1 or 0.00)
            res[obj.id]['tot_income_approx']= res[obj.id]['gross_tol_inc_approx'] - (obj.dec_und_sec and obj.dec_und_sec.total_ded or 0.00 + obj.ded_under_chp and obj.ded_under_chp.total_ded1 or 0.00)
            input_amt = 0
            input_amt_approx = 0
            input_amt = int(round(res[obj.id]['tot_income_']))
            input_amt_approx = int(round(res[obj.id]['tot_income_approx']))
            d1 = (input_amt % 10)
            d1_approx = (input_amt_approx % 10)
            if d1 == 0:
                input_amt = input_amt 
            else:
                if d1 > 5:
                    input_amt = input_amt + (10 - d1)
                else:
                    input_amt = input_amt - d1
            if d1_approx == 0:
                input_amt = input_amt 
            else:
                if d1_approx > 5:
                    input_amt_approx = input_amt_approx + (10 - d1_approx)
                else:
                    input_amt_approx = input_amt_approx - d1_approx

            res[obj.id]['tot_tax_inc']= input_amt
            res[obj.id]['tot_tax_inc_approx']= input_amt_approx
            total_income = 0.00
            total_income_approx=0.00
            gender = obj.gender
            rule_data = self.pool.get('income.tax.rule').search(cr,uid,[('gender','=',gender)])
            if not rule_data:
                raise osv.except_osv(_('Configration Error !'),
                        _('Can not find Tax Calculation Rule for this Gender Employee, Please Create Rule.'))
            else:
                total_income = res[obj.id]['tot_tax_inc']
                total_income_approx = res[obj.id]['tot_tax_inc_approx']
                rule_obj = self.pool.get('income.tax.rule').browse(cr,uid,rule_data,context)
                final_amt = self.cal_rule_tax(rule_obj[0], total_income)
                final_amt_approx = self.cal_rule_tax(rule_obj[0], total_income_approx)
                res[obj.id]['tax_on_tol'] = final_amt
                res[obj.id]['tax_on_tol_approx'] = final_amt_approx
            final_amt = 0.00
            final_amt_approx = 0.00
            if obj.surcharge.sur_amt < res[obj.id]['tax_on_tol']:
                final_amt = res[obj.id]['tax_on_tol'] + (res[obj.id]['tax_on_tol'] * (obj.surcharge.perc/100))
            else:
                final_amt = res[obj.id]['tax_on_tol']
            if obj.surcharge.sur_amt < res[obj.id]['tax_on_tol_approx']:
                final_amt_approx = res[obj.id]['tax_on_tol_approx'] + (res[obj.id]['tax_on_tol_approx'] * (obj.surcharge.perc/100))
            else:
                final_amt_approx = res[obj.id]['tax_on_tol_approx']
            res[obj.id]['tol_tax_pay']= final_amt
            res[obj.id]['tol_tax_pay_approx']= final_amt_approx
            res[obj.id]['add_edn_cess']=  res[obj.id]['tol_tax_pay'] + (res[obj.id]['tol_tax_pay']*(obj.edu_cess_perc/100))
            res[obj.id]['add_edn_cess_approx']=  res[obj.id]['tol_tax_pay_approx'] + (res[obj.id]['tol_tax_pay_approx']*(obj.edu_cess_perc/100))
            result=0.00
            for s_obj in obj.employee.slip_ids:
                tds_amt = 0.0
                for s_obj_l in s_obj.line_ids:
                    if s_obj_l.code == 'TDS':
                        result += s_obj_l.total

            res[obj.id]['net_tax_pay']= result
            res[obj.id]['net_tax_pay_approx']= result
            res[obj.id]['balance_tax'] = round(res[obj.id]['add_edn_cess'] - res[obj.id]['net_tax_pay'])
            res[obj.id]['balance_tax_approx'] = round(res[obj.id]['add_edn_cess_approx'] - res[obj.id]['net_tax_pay_approx'])
        return res

    def cal_rule_tax(self,rule_obj,amt):
        l=[]
        l_dict={}
        temp_amt = 0.00
        final_amt = 0.00
        for l in rule_obj.l_cat:
            l_dict[l.seq_no] = (l.st_amt,l.end_amt,l.perc)
        seq_l = l_dict.keys()
        for seq in seq_l:
            if seq != seq_l[0]:
                temp_amt += (l_dict[seq-1][1] - l_dict[seq-1][0]) * (l_dict[seq-1][2]/100)
            if amt > l_dict[seq][0] and amt <= l_dict[seq][1]:
                final_amt = ((amt - l_dict[seq][0])*(l_dict[seq][2]/100)) + temp_amt
                temp_amt =0.00
                break
        return final_amt

    _columns={
                'name': fields.char('Description', size=64, required=False, readonly=True, states={'draft': [('readonly', False)]}),
                'employee':fields.many2one('hr.employee','Employee',required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'year_detail' :fields.many2one('account.fiscalyear','Fiscal Year',required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'dob':fields.date('Date Of Birth',size=6,required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'gender': fields.selection([('male','Male'),('female','Female')], 'Gender',required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'esi':fields.char('ESI',size=20,readonly=True, states={'draft':[('readonly',False)]}),
                'pf' :fields.char('PF',size=20,readonly=True, states={'draft':[('readonly',False)]}),
                'pan_no':fields.char('Pan-No',size=20,required=True, readonly=True, states={'draft':[('readonly',False)]}),
                'state':fields.selection([('draft','Draft'),("confirm","Confirm"),('cancel','Cancel')],'State', readonly=True),
                'docs':fields.one2many('documents','it_rel_id','Documents', readonly=True, states={'draft':[('readonly',False)]}),
                'basic':fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Basic Salary',
                                       store={
                                        'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                        },multi='all'),  
                'gross_salary':fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Gross Salary',
                                               store={
                                        'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                        },multi='all',help="Gross Annual Income/Salary(include all allowances)"),
                'gross_salary_approx':fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Approx-Gross Salary',
                                               store={
                                        'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                        },multi='all',help="Gross Annual Income/Salary(include all allowances)"),
                'less':fields.many2one('cal.allowance.tax', 'Allowance',help="Less: Allowances exempt u/s 10(for Service Period)",readonly=True, states={'draft':[('readonly',False)]}),
                'income_head_salary': fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Income under the head salaries',
                                                      store={
                                                        'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                        },multi='all'),      
                'income_head_salary_approx': fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Income under the head salaries(Approx)',
                                                      store={
                                                        'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                        },multi='all'),              
        
                'add_any_other_income':fields.many2one('cal.interest.received.tax', 'Other Income',help="Add: Any other income from other sources",readonly=True, states={'draft':[('readonly',False),('required',True)]}),
                'income_other': fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'), string='Result(Head income + Other income):',
                                               store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),  
                'income_other_approx': fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'), string='Result(Head income + Other income)(Approx):',
                                               store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),      
    
                'inc_h_pro':fields.many2many('cal.house.property','name','it_id' ,'h_id','Income from house property',readonly=True, states={'draft':[('readonly',False)]}),
                'gross_tol_inc' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Gross Total Income',
                                                  store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                'gross_tol_inc_approx' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Gross Total Income(Approx)',
                                                  store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),

                'dec_und_sec':fields.many2one('cal.deduction.tax', 'Deduction Under 80C Lines',help='Less: Deduction under Sec  80C (Max Rs.1,00,000/-)',readonly=True, states={'draft':[('readonly',False),('required',True)]}),
                'ded_under_chp':fields.many2one('cal.deduction.6.a.tax','Deduction Under VI-A Lines',help='Less: Deduction under chapter VI A',readonly=True, states={'draft':[('readonly',False),('required',True)]}),
                'tot_income_' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Income',
                                              store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                'tot_income_approx' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Income(Approx)',
                                              store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),

                'tot_tax_inc' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Taxable Income'
                                                ,store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all',help='Total Taxable Income (Round off to nearest 10 rupees)'),
                'tot_tax_inc_approx' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Taxable Income(Approx)'
                                                ,store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all',help='Total Taxable Income (Round off to nearest 10 rupees)'),

                'tax_rule':fields.many2one('income.tax.rule','Applied Rule Detail',help='General Rules For Tax on Total Income',readonly=True, states={'draft':[('readonly',False),('required',True)]}),
                'tax_on_tol' :  fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Tax on Total Income',
                                                store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),     
                'tax_on_tol_approx' :  fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Tax on Total Income(Approx)',
                                                store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),       
  
                'surcharge' : fields.many2one('income.tax.surcharge','Surcharge',help='Surcharge on Total Taxable Income',readonly=True, states={'draft':[('readonly',False),('required',True)]}),
                'tol_tax_pay' :fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Tax Payable',
                                               store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                'tol_tax_pay_approx' :fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Total Tax Payable(Approx)',
                                               store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),

                'edu_cess_perc' : fields.float('Edn Cess Persc(%)',readonly=True, states={'draft':[('readonly',False)]}),
                'add_edn_cess' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Add: Edn Cess',
                                                 store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                'add_edn_cess_approx' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Add: Edn Cess (Approx)',
                                                 store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),

                'net_tax_pay' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Net Tax Payable(TDS)',
                                                store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                'net_tax_pay_approx' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Net Tax Payable(TDS)(Approx)',
                                                store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                                    
                'balance_tax' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Balance Tax Payable/Refundable',
                                                store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),
                'balance_tax_approx' : fields.function(_all_cal, method=True, digits_compute=dp.get_precision('Payroll'),string='Balance Tax Payable/Refundable(Approx)',
                                                store={
                                                      'cal.income.tax': (lambda self, cr, uid, ids, c={}: ids, None, 20),
                                                    },multi='all'),

            }
    _defaults={
              'edu_cess_perc': lambda *a: 3.00,
              'state': lambda *a: 'draft',
              'year_detail':lambda self,cr,uid,c: self.pool.get('account.fiscalyear').find(cr, uid),
              }

    def create(self, cr, uid, vals, context={}):
        for doc_line in vals['docs']:
            if doc_line[2]['state'] != 'done':
                raise osv.except_osv('Configuration Error', 'Document are not Fully verified,Please Verify it First.')
        ret_id = super(cal_income_tax, self).create(cr, uid, vals, context)
        for line in vals['docs']:
            self.pool.get('documents').write(cr, uid, line[1], {'it_rel_id': ret_id})
        return ret_id
    
    def write(self, cr, uid, ids, vals, context=None):
        return super(cal_income_tax, self).write(cr, uid, ids, vals, context=context)
   
    def tax_draft(self, cr, uid, ids,context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def tax_confirm(self, cr, uid, ids,context={}):
        self.write(cr, uid, ids, {'state':'confirm'})
        return True
    
    def tax_cancel(self, cr, uid, ids,context={}):
        if not ids:
            return False
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def _check_gender_rule(self, cr, uid, ids):
        obj_l=self.browse(cr,uid,ids)
        for obj in obj_l:
            if obj.gender != obj.tax_rule.gender:
                return False
        return True      
    
    _constraints = [
        (_check_gender_rule, 'Applied Rule Miss-match with employee Gender',['gender']),
    ]
    
cal_income_tax()    


class document_proof_type(osv.osv):
    _name="document.proof.type"
    _columns={
          'name':fields.char('Proof Type Name',size=64,required=True),
          'shortcut':fields.char('Shortcut',size=64,required=True),
          }
#End Class
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The name must be unique!'),
        ('shortcut_uniq', 'UNIQUE(shortcut)', 'The Shortcut must be unique!'),
    ]

document_proof_type()

def _doc_proof_type_get(self,cr,uid,context={}):
    obj = self.pool.get('document.proof.type')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['shortcut','name'], context)
    return [(r['shortcut'], r['name']) for r in res]

class documents(osv.osv):
    _name='documents'
    _description = "Document Detail"
    

    _columns = {
           'name': fields.char('Proof name',size=256,required=True),
           'emp_id':fields.many2one('hr.employee','Employee',required=True),
           'it_rel_id':fields.many2one('cal.income.tax','Income Tax'),
           'note':fields.text('Proof Note'),
           'document':fields.binary('Proof Document'),
           'type': fields.selection(_doc_proof_type_get,'Type',select=True),
           'state': fields.selection([
           ('draft','Draft'),
           ('apply','Under Varification'),
           ('done','Varified'),
           ('cancel','Cancel')
          ],'State', select=True),
      }
    
    _defaults = {
                     'state': lambda *a: 'draft',
                 }

    def create(self, cr, uid, vals, context={}):
        ret_id = super(documents, self).create(cr, uid, vals, context)
        s_rec_id = self.pool.get('cal.income.tax').search(cr,uid,[('employee','=',vals['emp_id'])])
        if s_rec_id:
            self.write(cr, uid, ret_id, {'it_rel_id': s_rec_id[0]})
        return ret_id

    def apply_draft(self, cr, uid, ids,context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def apply_varification(self, cr, uid, ids,context = {}):
        self.pool.get('documents').write(cr,uid,ids,{'state':'apply'})
        return True
    #end method
    def proof_varified(self,cr,uid,ids,context = {}):
        self.pool.get('documents').write(cr,uid,ids,{'state':'done'})
        return True
    #end Method
    def proof_canceled(self,cr,uid,ids,context = {}):
        self.pool.get('documents').write(cr,uid,ids,{'state':'cancel'})
        return True

    def reopen(self, cr, uid, ids,context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    #end Method

#End Class
documents()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
