#!/usr/bin/env python
#coding: utf-8

# (c) 2007 Sednacom <http://www.sednacom.fr>
# author : gael@sednacom.fr

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from osv import fields, osv
import time
from mx import DateTime as mdt
import tools

class hr_employee(osv.osv):
	_name = "hr.employee"
	_description = "Medical Exam"
	_inherit = "hr.employee"

	def button_confirm(self, cr, uid, ids, *args):
	# on verifie si le contrat n'a pas été deja reconduit	
		test =  self.pool.get('hr.employee').browse(cr, uid,ids[0])	
		if test.medic_exam:
			val={}
			val['last_medic_exam']=test.medic_exam
			renew = self.pool.get('hr.employee').write(cr, uid,ids[0],val)
	
		else:
			renew=False
		return renew 

	_columns = {
		'medic_exam_delay' : fields.integer('Medical examination delay (Years)'),
		'medic_exam_delay_alert' : fields.integer('Medical examination delay alert (Days)'),
		'medic_exam_alert' : fields.date('Medical examination alert'),
		'last_medic_exam' : fields.date('Last Medical examination date', readonly=True),
		'email_alert' : fields.char('Email for reporting', size=64),
	}
	_defaults = {
	'medic_exam_delay' : lambda *a : 1,
	'medic_exam_delay_alert' : lambda *a : 15,	
	}

	def onchange_for_date_end(self, cr, uid, ids, last_medic_exam, medic_exam_delay,medic_exam,medic_exam_delay_alert):
		if not last_medic_exam and medic_exam :
			alert_delay = medic_exam_delay_alert
			medic_exam = mdt.DateTime(int(medic_exam[0:4]),int(medic_exam[5:7]),int(medic_exam[8:10]))
			date = str(medic_exam.year) + '-' + str(medic_exam.month) + '-' + str(medic_exam.day)		
			if alert_delay :
				date_alert = medic_exam - alert_delay * mdt.oneDay
				date_alert = str(date_alert.year) + '-' + str(date_alert.month) + '-' + str(date_alert.day)			
			return {'value':{'medic_exam': date, 'medic_exam_alert' : date_alert}}			
		elif not last_medic_exam and not medic_exam :		
			return {}
		else:
			alert_delay = medic_exam_delay_alert	
			medic_exam = mdt.DateTime(int(last_medic_exam[0:4]),int(last_medic_exam[5:7]),int(last_medic_exam[8:10])) + medic_exam_delay * mdt.RelativeDate(years=1)	
			date = str(medic_exam.year) + '-' + str(medic_exam.month) + '-' + str(medic_exam.day)		
			if alert_delay :
				date_alert = medic_exam - alert_delay * mdt.oneDay
				date_alert = str(date_alert.year) + '-' + str(date_alert.month) + '-' + str(date_alert.day)			
			return {'value':{'medic_exam': date, 'medic_exam_alert' : date_alert}}

	def _check(self, cr, uid, context={}):
		req = cr.execute("SELECT DISTINCT email_alert FROM hr_employee WHERE email_alert is not null")	
		mails = cr.dictfetchall(req)
		emails=[]		
		for mail in mails:	
			req = cr.execute("SELECT name, medic_exam, last_medic_exam, medic_exam_alert FROM hr_employee WHERE medic_exam_alert < NOW() and email_alert=%s",(mail['email_alert'],))
			res = cr.dictfetchall(req)
			email=[]		
			if res :		
				email.append(mail['email_alert'])
				body="liste des visites médicales à passer\n"
				body+="-----------------------------------------------------------\n"
				body+="| date alerte | date visite   | Nom\n"					
				for line in res:				
					body+="| "+line['medic_exam_alert']+"  | "+line['medic_exam']+"    | "+line['name']+"\n"
				body+="-----------------------------------------------------------\n"
				body+="Cette email a été envoyé par tinyerp sur :"+mail['email_alert']+"\n"
				email_from = "contact@sednacom.fr"
				subject = "Alerte Visite Médicale"			
				#print body
				email_cc= False
				email_bcc=False
				on_error=False
				reply_to=False
				attach=None 
				tinycrm=False
				"""Send an email."""
				#print "Run medical exam Cron"			
				tools.email_send(email_from, email, subject, body, email_cc=None, email_bcc=None, on_error=False, reply_to=False, tinycrm=False)

		return True

hr_employee()


