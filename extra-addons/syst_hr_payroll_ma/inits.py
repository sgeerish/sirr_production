'''
Created on 28 sept. 2010

@author: ahmed
'''
from account import invoice
from osv import fields, osv

class systemum_employee(osv.osv):
    _inherit = 'hr.employee'
    _auto = False

    def __init__(self, pool, cr):
        super(systemum_employee, self).__init__(pool, cr)
        arch="""<?xml version="1.0"?>
            <page string="Personal Information" position="after">
                    <page string="Miscellaneous">
                        <group colspan="2" col="2">
                        <separator string="Personal Info" colspan="2"/>
                        <field name="bank_account_id"/>
                        <field name="place_of_birth"/>
                        <field name="children"/>
                        </group>
                        <group colspan="2" col="2">
                        <separator string="Job Info" colspan="2"/>
                        <field name="manager"/>
                        <field name="vehicle"/>
                        <field name="vehicle_distance"/>
                        </group>
                        <separator colspan="4" string="Prime Anciennete" />
                        <field name="date" required="1" />
                        <field name="anciennete" />
                        <separator colspan="4" string="Calcul IR" />
                        <field name="chargefam" />
                        <field name="logement" />
                        <separator colspan="4" string="Informations sur la banque" />
                        <field name="mode_reglement" />
                        <field name="compte" />
                        <field name="bank" />                       
                    </page>
                    <page string="Contracts">
                        <field colspan="4" name="contract_ids" nolabel="1"/>
                    </page>
            </page>
            """
	arch="""<?xml version="1.0"?>
            <page string="Personal Information" position="after">
                    <page string="Miscellaneous">
                        <group colspan="2" col="2">
                        <separator string="Personal Info" colspan="2"/>
                        <field name="bank_account_id"/>
                        <field name="place_of_birth"/>
                        <field name="children"/>
                        </group>
                        <group colspan="2" col="2">
                        <separator string="Job Info" colspan="2"/>
                        <field name="manager"/>
                        <field name="vehicle"/>
                        <field name="vehicle_distance"/>
                        </group>
                        <separator colspan="4" string="Prime Anciennete" />
                        <field name="date" required="1" />
                        <field name="anciennete" />
                        <separator colspan="4" string="Calcul IR" />
                        <field name="chargefam" />
                        <field name="logement" />
</page>
<page string="Banque">
                        <separator colspan="4" string="Informations sur la banque" />
                        <field name="mode_reglement" />
                        <field name="compte" />
                        <field name="bank" />      
<newline/>
                        <field name="loan" />                       
                    </page>
                    <page string="Sanctions">
                        <field colspan="4" name="sanction_ids" nolabel="1">
<tree>
                        <field colspan="4" name="name" />
                        <field colspan="4" name="date" />
</tree>
</field>
                    </page>
                    <page string="Medicale">
                        <field colspan="4" name="medical_ids" nolabel="1">
<tree>
                        <field colspan="4" name="name" />
                        <field colspan="4" name="date" />
</tree>
</field>
                    </page>
                    <page string="Qualifications">
                        <field colspan="4" name="qualification_ids" nolabel="1"/>
                    </page>
                    <page string="Contracts">
                        <field colspan="4" name="contract_ids" nolabel="1"/>
                    </page>
            </page>
            
	"""
        sql = '''
        Update ir_ui_view set arch = %s Where model='hr.employee' and name='hr.hr.employee.view.form2'
        '''
        cr.execute(sql, (arch,))
        employee='''<?xml version="1.0"?>
        <form string="Employee">
                    <group colspan="4" col="8">
                        <group colspan="6" col="6">
                        <field colspan="6" name="name"/>
                        <field name="user_id" on_change="onchange_user(user_id)"/>
                        <field name="company_id" widget="selection" groups="base.group_multi_company,base.group_extended" on_change="onchange_company(company_id)"/>
                        <field name="active" groups="base.group_extended"/>
                        <newline/>
                        <field name="department_id" widget="selection" on_change="onchange_department(department_id)"/>
                        <field name="parent_id"/>
                        <field name="matricule" />
                        <field name="cin" />
                        <field name="affilie" string="Affilie" />
                        </group>
                        <group colspan="2" col="1">
                        <field name="photo" widget="image" nolabel="1"/>
                        </group>
                    </group>
                    <notebook colspan="6">
                        <page string="Personal Information">
                            <group col="2" colspan="2">
                                <separator colspan="2" string="Social IDs"/>
                                <field name="ssnid" string="Matricule CNSS" />
                                <field name="sinid" groups="base.group_extended" string="Matricule CIMR" />
                                <field name="identification_id" groups="base.group_extended" string="Autre identifiant"/>
                                <field name="passport_id"/>
                            </group>
                            <group col="2" colspan="2">
                                <separator string="Status" colspan="2"/>
                                <field name="gender"/>
                                <field name="marital" widget="selection"/>
                                <field name="country_id"/>
                                <field name="birthday"/>
                            </group>
                            <group col="2" colspan="2">
                                <separator string="Contact Information" colspan="2"/>
                                <field name="address_home" colspan="2"/>
                                <field name="address"/>
                                <field name="work_phone" readonly="False"/>
                                <field name="phone_home" />
                                <field name="work_email" widget="email"/>
                                <field name="work_location"/>
                            </group>
                            <group col="2" colspan="2">
                                <separator string="Position" colspan="2"/>
                                <field name="job_id" domain="[('state','!=','old')]"/>
                                <field name="coach_id"/>
                            </group>
                        </page>
                        <page string="Categories">
                            <field name="category_ids" nolabel="1"/>
                        </page>
                        <page string="Notes">
                            <field colspan="4" nolabel="1" name="notes"/>
                        </page>
                    </notebook>
                </form>'''
        sql2="Update ir_ui_view set arch = %s Where model='hr.employee' and name='hr.employee.form'"
        cr.execute(sql2, (employee,))
systemum_employee()
class systemum_contract(osv.osv):
    _inherit = 'hr.contract'
    _auto = False

    def __init__(self, pool, cr):
        super(systemum_contract, self).__init__(pool, cr)   
        contract='''<?xml version="1.0"?>
                <form string="Contract">
                    <group colspan="3" col="6">
                    <field name="name"/>
                    <field name="employee_id"/>
                    <field name="job_id"/>
                    <field name="wage"/>
                    <field name="wage_type_id" widget="selection"/>
                    <field name="type_id" widget="selection"/>
                    <field name="cotisation" />
                    <button name="net_to_brute" string="Net > Brute" type="object" icon="gtk-execute" />
                    </group>
                    <notebook>
                    <page string="Information">
                        <group col="2" colspan="2">
                        <separator colspan="2" string="Duration"/>
                        <field name="date_start"/>
                        <field name="date_end"/>
                        <field name="working_hours"/>
                        </group>                 
                        <group col="2" colspan="2">
                        <separator colspan="2" string="Trial Period"/> 
                        <field name="trial_date_start"/>
                        <field name="trial_date_end"/>
                        </group>
                        <separator string="Salaire horaire" colspan="4"/>
                        <field name="monthly_hour_number" />
                        <field name="hour_salary" />
                        <separator colspan="4" string="Notes"/>
                        <field colspan="4" name="notes" nolabel="1"/>
                    </page>
                    <page string="Les rubriques">
                            <field colspan="4" name="rubrique_ids" nolabel="1"
                                widget="one2many_list">
                                <form string="Lignes rubriques">
                                    <group col="6" colspan="4">
                                        <field name="rubrique_id" />
                                        <field name="montant" />
					                    <field name="taux" />
                                        <field name="permanent" />
                                    </group>
                                    <group col="6" colspan="4"
                                        attrs="{'invisible':[('permanent','==',True)]}">

                                        <field name="period_id" on_change="onchange_period_id(period_id)" />
                                        <field name="date_start" />
                                        <field name="date_stop" />
                                    </group>
                                </form>
                            </field>
                        </page>
                    </notebook>
                </form>'''
        sql="Update ir_ui_view set arch = %s Where model='hr.contract' and name='hr.contract.view.form'"
        cr.execute(sql, (contract,))
systemum_contract()  
