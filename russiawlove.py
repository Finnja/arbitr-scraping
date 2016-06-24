# -*- coding: utf-8 -*-

from datetime import date, timedelta
import time
import urllib2
import csv
import os

# selenium packages
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# .pdf to .csv
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
  
from pdfminer.converter import LTChar, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

##############
### OOP MF ###
##############

class case(object):
	"""Class that holds all the information about a case"""
	
	def __init__(self, case_id):
		super(case, self).__init__()
		self.case_id = case_id
		self.pdf_name = self.case_id.replace('/', '-') + '.pdf'
		self.txt_name = self.case_id.replace('/', '-') + '.txt'

	###########################
	### Selenium operations ###
	########################### 	

	def web(self, driver):
		""" Gathers the web variables from the case card page
		"""

		# web data collection #
		self.pWithdrew(driver)
		self.caseHeard(driver)

		self.caseType(driver)
		self.plaintiff(driver)
		self.defendant(driver)
		self.thirdParties(driver)
		self.dateFiled(driver)
		self.dateDecision(driver)
		self.appealedAndUpheld(driver)
		self.type()
		self.court_and_judge(driver)
		self.settled(driver)
		
		self.getPDF(driver)
		self.typeCourtDoc()

		pass

	def text(self):
		if self.PW == 'Check text':
			self.pwText()

		if self.SoC == 'Check text':
			self.settledText()

		self.categoryOfComplaint()
		self.simpProcedures()
		self.defendCC()
		self.plaintAppeared()
		self.defAppeared()


		pass


	######################
	### CSV Operations ###
	######################

	def data_to_csv(self):

		# Logic to organize plaintiffs and defendants

		# Defendants
		if len(self.definfo.keys()) > 2:
			self.d1 = str(self.definfo.keys()[0].encode('utf-8'))
			self.d1add = str(self.definfo.values()[0].encode('utf-8'))
			self.d1type = str(self.TD[self.definfo.keys()[0]].encode('utf-8'))

			self.d2 = str(self.definfo.keys()[1].encode('utf-8'))
			self.d2add = str(self.definfo.values()[1].encode('utf-8'))
			self.d2type = str(self.TD[self.definfo.keys()[1]].encode('utf-8'))

			self.d3 = str(self.definfo.keys()[2].encode('utf-8'))
			self.d3add = str(self.definfo.values()[2].encode('utf-8'))
			self.d3type = str(self.TD[self.definfo.keys()[2]].encode('utf-8'))

			# concatonate the rest of the defendants into a comma-separated string
			self.rest_of_def = ''
			for i in self.definfo.keys()[3:]:
				self.rest_of_def += (', ' + str(i.encode('utf-8')))

		elif len(self.definfo.keys()) > 1:
			self.d1 = str(self.definfo.keys()[0].encode('utf-8'))
			self.d1add = str(self.definfo.values()[0].encode('utf-8'))
			self.d1type = str(self.TD[self.definfo.keys()[0]].encode('utf-8'))

			self.d2 = str(self.definfo.keys()[1].encode('utf-8'))
			self.d2add = str(self.definfo.values()[1].encode('utf-8'))
			self.d2type = str(self.TD[self.definfo.keys()[1]].encode('utf-8'))

			self.d3, self.d3add, self.d3type, self.rest_of_def = ('N/A',)*4

		else:
			self.d1 = str(self.definfo.keys()[0].encode('utf-8'))
			self.d1add = str(self.definfo.values()[0].encode('utf-8'))
			self.d1type = str(self.TD[self.definfo.keys()[0]].encode('utf-8'))

			self.d2, self.d2add, self.d2type, self.d3, self.d3add, self.d3type, self.rest_of_def = ('N/A',)*7

		# Plaintiffs
		if len(self.plaintinfo.keys()) > 2:
			self.p1 = str(self.plaintinfo.keys()[0].encode('utf-8'))
			self.p1add = str(self.plaintinfo.values()[0].encode('utf-8'))
			self.p1type = str(self.TP[self.plaintinfo.keys()[0]].encode('utf-8'))

			self.p2 = str(self.plaintinfo.keys()[1].encode('utf-8'))
			self.p2add = str(self.plaintinfo.values()[1].encode('utf-8'))
			self.p2type = str(self.TP[self.plaintinfo.keys()[1]].encode('utf-8'))

			self.p3 = str(self.plaintinfo.keys()[2].encode('utf-8'))
			self.p3add = str(self.plaintinfo.values()[2].encode('utf-8'))
			self.p3type = str(self.TP[self.plaintinfo.keys()[2]].encode('utf-8'))

			# concatonate the rest of the plaintiffs into a comma-separated string
			self.rest_of_plaint = ''
			for i in self.plaintinfo.keys()[3:]:
				self.rest_of_plaint += (', ' + str(i.encode('utf-8')))

		elif len(self.plaintinfo.keys()) > 1:
			self.p1 = str(self.plaintinfo.keys()[0].encode('utf-8'))
			self.p1add = str(self.plaintinfo.values()[0].encode('utf-8'))
			self.p1type = str(self.TP[self.plaintinfo.keys()[0]].encode('utf-8'))

			self.p2 = str(self.plaintinfo.keys()[1].encode('utf-8'))
			self.p2add = str(self.plaintinfo.values()[1].encode('utf-8'))
			self.p2type = str(self.TP[self.plaintinfo.keys()[1]].encode('utf-8'))

			self.p3, self.p3add, self.p3type, self.rest_of_plaint = ('N/A',)*4

		else:
			self.p1 = str(self.plaintinfo.keys()[0].encode('utf-8'))
			self.p1add = str(self.plaintinfo.values()[0].encode('utf-8'))
			self.p1type = str(self.TP[self.plaintinfo.keys()[0]].encode('utf-8'))

			self.p2, self.p2add, self.p2type, self.p3, self.p3add, self.p3type, self.rest_of_plaint = ('N/A',)*7

		# Write header for .csv file
		with open('test.csv', 'a+') as csvfile:
			fieldnames = ['Case ID', 'Case Type', 'Court', 'Judge', 'Judge Gender', 
						
						'Plaintiff 1', 'P1 Address', 'P1 Type',
						'Plaintiff 2', 'P2 Address', 'P2 Type',
						'Plaintiff 3', 'P3 Address', 'P3 Type',
						'Rest of Plaintiffs',

						'Defendant 1', 'D1 Address', 'D1 Type',
						'Defendant 2', 'D2 Address', 'D2 Type', 
						'Defendant 3', 'D3 Address', 'D3 Type',
						'Rest of Defendants',

						'Date Filed', 'Date Decision', 'Case Length', 'Type Court Doc', 
						'Category of Complaint', 'Simplified Procedures?', 'Def Contesting', 
						'Plaintiff Appeared?', 'Defendant Appeared?']

			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			if self.first_row:
				writer.writeheader()
			
			writer.writerow({'Case ID': str(self.case_id),
				'Case Type': str(self.CT),
				'Court': str(self.court.encode('utf-8')),
				'Judge': str(self.judge.encode('utf-8')),
				'Judge Gender': str(self.judge_gender.encode('utf-8')),
				
				# Plaintiffs 1-3 and their info
				'Plaintiff 1': self.p1, 
				'P1 Address': self.p1add, 
				'P1 Type': self.p1type,

				'Plaintiff 2': self.p2, 
				'P2 Address': self.p2add, 
				'P2 Type': self.p2type,

				'Plaintiff 3': self.p3, 
				'P3 Address': self.p3add, 
				'P3 Type': self.p3type,

				'Rest of Plaintiffs': self.rest_of_plaint,

				# Defendants 1-3 and their info
				'Defendant 1': self.d1, 
				'D1 Address': self.d1add, 
				'D1 Type': self.d1type,

				'Defendant 2': self.d2, 
				'D2 Address': self.d2add, 
				'D2 Type': self.d2type,

				'Defendant 3': self.d3, 
				'D3 Address': self.d3add, 
				'D3 Type': self.d3type,

				'Rest of Defendants': self.rest_of_def,

				'Date Filed': str(self.df), 
				'Date Decision': str(self.decisiondate),
				'Case Length': str(self.caselength.days) + ' days',
				'Type Court Doc': str(self.tcd),
				'Category of Complaint': str(self.coc.encode('utf-8')), 
				'Simplified Procedures?': str(self.sp), 
				'Def Contesting': str(self.dcc), 
				'Plaintiff Appeared?': str(self.pappeared), 
				'Defendant Appeared?': str(self.dappeared) 
				})



	#####################
	### Web variables ###
	#####################

	def getPDF(self, driver):
		"""Downloads PDF once on the page of a court case """
		
		rows = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div')
		for row in rows:
			heading = row.find_element_by_xpath('.//div/div/strong')
			if heading.text == u'Первая инстанция':
				pdf_url = row.find_element_by_xpath('.//div/div/h2/a').get_attribute("href")

		self.pdf_url = pdf_url

		response = urllib2.urlopen(pdf_url)
		FILE = open(self.pdf_name, "wb")
		FILE.write(response.read())
		FILE.close()

		print('PDF download complete')

	def court_and_judge(self, driver):
		""" Finds and stores the court and judge given a case number. Also determines gender of judge
		"""
		court_tab = driver.find_element_by_xpath("id('case_judges')")
		court_tab.click()

		court = driver.find_element_by_xpath('//*[@id="gr_case_judges"]/table/thead/tr/td/div/a')
		self.court = court.text

		judge = driver.find_element_by_xpath('//*[@id="gr_case_judges"]/table/tbody/tr/td/div/ul/li')
		self.judge = judge.text

		name = max(self.judge.split(), key=len)
		if name[-1] in u'яа':
			self.judge_gender = 'Female'
		elif name[-1] == u'о':
			self.judge_gender = 'N/A'
		else:
			self.judge_gender = 'Male'


	def defendant(self, driver):
		""" Finds all of the defendants and stores them and their address in a dictionary
		"""
		self.definfo = {}
		defend = driver.find_elements_by_xpath('//*[@id="gr_case_partps"]/table/tbody/tr/td[2]/div/ul/li')
		for dant in defend:
			address = dant.find_element_by_xpath('.//span/span').get_attribute("innerHTML")
			self.definfo[dant.text] = address


	def plaintiff(self, driver):
		""" Finds all of the plaintiffs and stores them and their address in a dictionary
		"""
		self.plaintinfo = {}
		plaint = driver.find_elements_by_xpath('//*[@id="gr_case_partps"]/table/tbody/tr/td[1]/div/ul/li')

		for tiff in plaint:
			address = tiff.find_element_by_xpath('.//span/span').get_attribute("innerHTML")
			self.plaintinfo[tiff.text] = address

	def thirdParties(self, driver):
		""" Finds and stores all 3rd parties
		"""
		self.tps = []
		tp = driver.find_elements_by_xpath('//*[@id="gr_case_partps"]/table/tbody/tr/td[3]/div/ul/li')
		for party in tp:
			self.tps.append(party.text)

	def dateFiled(self, driver):
		""" Finds the date filed, converts it from text to a datetime object, and stores
		"""
		dateF = driver.find_element_by_xpath('//*[@id="b-case-header"]/ul[2]/li[2]/a').get_attribute("innerHTML")
		L = dateF.split()
		months = {
			u'января': 1,
			u'февраля': 2,
			u'марта': 3,
			u'апреля': 4,
			u'мая': 5,
			u'июня': 6,
			u'июля': 7,
			u'августа': 8,
			u'сентября': 9,
			u'октября': 10,
			u'ноября': 11,
			u'декабря': 12
		}

		self.df = date(int(L[2]), months[L[1]], int(L[0]))


	def dateDecision(self, driver):
		"""Determines date decision was filed """
		headings = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div/div/div/strong')
		for heading in headings:
			if heading.text == u'Первая инстанция':
				dd = heading.find_element_by_xpath('.//following-sibling::span')
				break
		dd = dd.text
		
		self.decisiondate = date(int(dd[6:]), int(dd[3:5]), int(dd[0:2]))

		self.caselength = self.decisiondate - self.df

	def caseType(self, driver):
		"""Determines the type of the case (administrative, civil, or bankruptcy)
		"""
		icon = driver.find_element_by_xpath('//*[@id="b-container"]/div[1]/dl/dt/span/i')
		cat = icon.get_attribute("class").strip()[7:]
		if cat != u'':
			self.CT = cat
		else:
			self.CT = 'other'

	def appealedAndUpheld(self, driver):
		""" Determines whether or not a case was appealed by looking at the titles of hearings
		"""
		headings = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div/div/div/strong')
		
		self.appealed = 'No'
		self.upheld = 'N/A'
		
		upheldString = u'Оставить без изменения решение, а апелляционную жалобу - без удовлетворения'

		rows = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div')
		for row in rows:
			heading = row.find_element_by_xpath('.//div/div/strong')
			if heading.text == u'Апелляционная инстанция':
				self.appealed = 'Yes'
				self.upheld = 'No'
				PDFTitle = row.find_element_by_xpath('.//div/div/h2/a')
				if upheldString in PDFTitle.text:
					self.upheld = 'Yes'
					break

	def caseHeard(self, driver):
		"""Checks a set of keywords to see if the case was heard by the judge """
		caseNotHeard = [u'об оставлении искового заявления (заявления) без рассмотрения', 
			u'определение об оставлении искового заявления (заявления) без рассмотрения', 
			u'о возвращении искового заявления', 
			u'о возвращении заявления', 
			u'возвратить заявление', 
			u'о передаче дела на рассмотрение другого арбитражного суда', 
			u'оставить без рассмотрения заявление']

		self.CH = 'Yes'

		titles = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div/div/div/h2/a')
		for title in titles:
			title = title.text.lower()
			for phrase in caseNotHeard:
				if phrase in title:
					self.CH = 'No'
					break

	def pWithdrew(self, driver):
		"""Similar to above, checks case title keywords to see if the plaintiff withdrew"""

		check_text = [u'о прекращении производства по делу', u'принять отказ от иска', 
			u'о возвращении искового заявления', u'прекратить производство по делу', 
			u'возвратить заявление'] 

		rows = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div')
		
		for row in rows:
			heading = row.find_element_by_xpath('.//div/div/strong')
			
			if heading.text == u'Первая инстанция':
				PDFTitle = row.find_element_by_xpath('.//div/div/h2/a').text.lower()
				for phrase in check_text:
					if phrase in PDFTitle:
						self.PW = 'Check text'
						return
	
		self.PW = 'No'

	def settled(self, driver):
		"""Checks decision titles for a phrase that signifies that the case
		was settled. If that keyword is found, a search of the document is conducted to
		confirm. """

		keyphrase = u'определение о прекращении производства по делу'

		rows = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div')
		
		for row in rows:
			heading = row.find_element_by_xpath('.//div/div/strong')
			
			if heading.text == u'Первая инстанция':
				PDFTitle = row.find_element_by_xpath('.//div/div/h2/a').text.lower()
				if keyphrase in PDFTitle:
					self.SoC = 'Check text'
					return

		self.SoC = 'No'

	def rulingForP(self, driver):
		"""Determines if the court ruled in favor of the plaintiff
		0: loss, 1: partial win, 2: full win
		bankruptcy cases are automatically coded as 'NA' """

		if self.CT == 'bankruptcy':
			self.result = 'N/A'

		else:

			rows = driver.find_elements_by_xpath('//*[@id="chrono_list_content"]/div/div')

			try:
				for row in rows:
					heading = row.find_element_by_xpath('.//div/div/strong')
					
					if heading.text == u'Первая инстанция':
						PDFTitle = row.find_element_by_xpath('.//div/div/h2/a').text.lower()
			except:
				print('CORRECT DECISION NOT FOUND')
			
			if self.CT == 'civil':
			
				keyword_dict = {u'иск удовлетворить полностью': 'Yes', 
					u'иск удовлетворить частично': 'Partly',
					u'иск удовлетворить частично или полностью': 'partial or full win (categories collapsed)',
					u'в иске отказать полностью': 'No',
					u'отказать в иске': 'No'}

				for key in keyword_dict:
					if key in PDFTitle:
						self.result = keyword_dict[key]
						return

			else:

				keyword_dict = {'Yes': [u'признать ненормативный правовой акт недействительным в части',
					u'признать ненормативный правовой акт недействительным полностью',
					u'признать решения и действия (бездействия) незаконными полностью',
					u'иск удовлетворить полностью',
					u'признать решение адм. органа незаконным и отменить его полностью',
					u'привлечь к административной ответственности',
					u'взыскать обязательные платежи и санкции'],

					'No': [u'признать решение административного органа законным и отказать в удовлетворении требований заявителя',
					u'в иске отказать полностью',
					u'отказать в признании решения и действий (бездействий) незаконными полностью',
					u'признать решение адм. органа незаконным и отменить его полностью',
					u'отказать в признании ненормативного правового акта недействительным']}

				for key in keyword_dict:
					for phrase in keyword_dict[key]:
						if phrase in PDFTitle:
							self.result = key
							return


		self.result = 'error'





	#######################
	### Misc. variables ###
	#######################

	def type(self):
		""" Checks and sets type of plaintiff and defendant"""
		self.TD = {}
		self.TP = {}
		for defend in self.definfo.keys():
			self.TD[defend] = typeOf(defend)

		for plaint in self.plaintinfo.keys():
			self.TP[plaint] = typeOf(plaint)

	def typeCourtDoc(self):
		"""Looks in pdf url to set the type of court document (opredelenie/reshenie)"""

		if 'Opredelenie' in self.pdf_url:
			self.tcd = 0
		else:
			self.tcd = 1


	######################
	### Text variables ###
	######################

	def categoryOfComplaint(self):
		"""Determines, given a set of key phrases, the category of the plaintiff's complaint.
		This is the big one -- probably not going to end up using the function in the long run."""

		if self.CT == 'bankruptcy':
			self.coc = u'признании несостоятельным'
			return
		
		elif self.CT == 'civil':
			insurance = False
			
			# playerTypes = self.TP.values() + self.TD.values()
			# for i in playerTypes:
			# 	if i in [u'СК', u'ОСАО']:
			# 		insurance = True

			if not insurance:
				playerNames = self.TP.keys() + self.TD.keys()
				insuranceKeywords = [u'страховая', u'страховой', u'страх', u'СК', u'ОСАО']
				for j in playerNames:
					for k in insuranceKeywords:
						if k in j:
							insurance = True
			if insurance:
				self.coc = u'взыскании страхового возмещения'
				return

			else:
				D = { # civil keyword dict
					u'взыскании задолженности': ['о взыскании задолженности',
						'о взыскании неустойки', 
						'составляющих задолженность',
						'о взыскании суммы задолженности',
						'о взыскании процентов',
						'пользование чужими денежными средствами',
						'задолженности по договору', 
						'убытков в порядке суброгации',
						'о взыскании суммы гарантийного удержания',
						'долга',
						'долг',
						'задолженности',
						'задолженность',
						'о взыскании пени'],
					u'взыскании страхового возмещения': ['о взыскании суммы страхового возмещения', 'взыскании страхового возмещения', 'страхового возмещения'],
					u'о признании права собственности': ['о признании права собственности', 'о признании права государственной собственности','о признании права федеральной собственности'],
					u'о расторжении договора': ['о расторжении договора', 'о признании договора прекращенным'],
					u'o признании договоров недействительными': ['о признании совершенной ничтожной односторонней сделки по отказу от исполнения договора аренды недействительной',
						'о признании договора недействительным'],
					u'o признании недействительной сделки': ['признании недействительной сделки', 'признании сделки частично недействительной'],
					u'о защите деловой репутации': ['о защите деловой репутации'],
					u'нарушение прав интелектуальной собственности': ['за нарушение исключительных имущественных прав',
						'незаконное использование товарного знака',
						'нарушения исключительного права',
						'о признании исключительного права',
						'исключительного права',
						'исключительное право',
						'нарушение прав интелектуальной собственности'],
					u'О выселении из помещения': ['о выселении ответчика из нежилого помещения', 'о прекращении обязательств по договору аренды и выселении'],
					u'об освобождении земельного участка': ['об освобождении земельного участка'],
					u'о взыскании убытков': ['в возмещение убытков', 'о взыскании убытков'],
					u'o взыскании неосновательного обогащения': ['взыскании неосновательного обогащения'],
					u'спор, связанный с ценными бумагами': ['спор, связанный с ценными бумагами','за неплатеж по векселям', 'выпуск ценных бумаг'],
					u'спор, связанный с Государственной регистрацией': ['о признании недействительными записей в ЕГРЮЛ',
						'спор, связанный с Государственной регистрацией'],
					u'понуждении совершить действия': ['о понуждении совершить действия'],
					u'о замене взыскателя': ['о замене взыскателя'],
					u'о признании незаконным бездействия': ['о признании незаконным бездействия'],
					u'конфликт между участниками общества': ['конфликт между участниками общества', 'собрания участников общества',
						'собраниe участников общества']
			}
		elif self.CT == 'administrative':
			if ('gov' not in self.TP.values()) and ('gov' in self.TD.values()): # ADD EXEMPTION FOR TAX AGENCIES
				self.coc = u'об оспаривании ненорматив. правовых актов иных гос органов'
				return

			elif (u'ИФНС' in self.TP.values()) or (u'Налоговая служба' in self.TP.keys()):
				keyphrases = ['о взыскании штрафа', 'о привлечении к административной ответственности', 'о взыскании штрафных санкций', 'обязательное пенсионное страхование']
				with open(self.txtfile) as searchfile:
					lines = searchfile.read()
					for phrase in keyphrases:
						if lines.find(phrase):
							self.coc = u'о взыскании с организаций и граждан иными гос органами'
							return		

			D = { # administrative keyword dict
				u'об оспаривании ненорматив. правовых актов налоговых органов': ['налоговая служба', 'ифнс'],
				u'о взыскании с организаций и граждан иными гос органами': ['о взыскании штрафа', 'о привлечении к административной ответственности',
					'о взыскании штрафных санкций', 'обязательное пенсионное страхование'],
				u'о прекращении исполнительного производства': ['о прекращении исполнительного производства'],
				u'об обязании выдать разрешение на организацию и обустройство земельного участка': ['об обязании выдать разрешение на организацию и обустройство земельного участка'],
				u'о признании недействительными постановлений': ['о признании недействительными постановлений', 'о признании незаконным и отмене постановления'],
				u'Об ануллирование лицензии': ['Аннулирование лицензии'],
				u'взыскание предмет залога / о восстановлении права залога': ['взыскания на заложенное', 'о восстановлении права залога', 'заложенное', 'залог'],
				u'о признании незаконным постановления судебного пристава': ['судебных приставов', 'судебный пристав']
			}

		else:
			D = { # other keyword dict
				u'о выдаче исполнительного листа на принудительное исполнение решения третейского суда': ['третейского суда', 'третейский суд'],
				u'установлении факта имеющего юридическое значение': ['установлении факта имеющего юридическое значение'],
				u'о вручении документов': ['о вручении документов']
			}

		with open(self.txt_name) as searchfile:
			lines = searchfile.read()
			for key in D:
				for phrase in D[key]:
					if lines.find(phrase) > 0:
						self.coc = key
						return
		
		if self.CH == 'No' or self.PW == 'Yes':
			self.coc = 'N/A'
		else:
			self.coc = 'COC ERROR'

	def simpProcedures(self):
		"""Scans text looking for phrase indicating that simplified procedures were used"""
		with open(self.txt_name) as searchfile:
			lines = searchfile.read()
			if lines.find('упрощенное производство') > 0 or lines.find('упрошенного производства') > 0:
				self.sp = True
				return

		self.sp = False

	def defendCC(self):
		"""Looks for keyword to see if defendant is contesting complaint"""
		L = [u'ответчиком отзыв не представлен',
		u'ответчик, извещенный в порядке статьи 123 арбитражного процессуального кодекса российской федерации, явку своего представителя не обеспечил',
		u'ответчик отзыв на иск не представил',
		u'адресат не явился за получением копии судебного акта',
		u'заинтересованное лицо в отзыве на заявление признало задолженность в полном объеме']

		for phrase in L:
			if self.txt_name.find(phrase) != -1:
				self.dcc = False # If any of these phrases appear, the defendant is NOT contesting the complaint
		self.dcc = True

	def plaintAppeared(self):
		"""checks a few phrases + their placement in the text to see if the plaintiff showed up"""
		noShow = [ 'лица, участвующие в деле, не явились',
		'лица, участвующие в деле, в судебное заседание не явились',
		'стороны не явились',
		'ходатайство о рассмотрении дела в отсутствие представителя']

		with open(self.txt_name) as searchfile:
			lines = searchfile.read()
			a = lines.find('от истца')
			b = lines.find('от заявителя')

			if a > 0:
				if 'не явился' in lines[a:(a+100)] or 'извещен' in lines[a:(a+100)]:
					self.pappeared = False
				else:
					self.pappeared = True
			elif b > 0:
				if 'не явился' in lines[b:(b+100)] or 'извещен' in lines[b:(b+100)]:
					self.pappeared = False
				else:
					self.pappeared = True
			elif lines.find('при участии представителя истца') > 0:
				self.pappeared = True
			else:
				for phrase in noShow:
					if lines.find(phrase) > 0:
						self.pappeared = False
				self.pappeared = 'Uncertain'

	def defAppeared(self):
		"""Similar to above for the defendant, not the cleanest of functions"""
		noShow = [ 'лица, участвующие в деле, не явились',
		'лица, участвующие в деле, в судебное заседание не явились',
		'стороны не явились',
		'ходатайство о рассмотрении дела в отсутствие представителя']

		with open(self.txt_name) as searchfile:
			lines = searchfile.read()
			a = lines.find('от ответчик')
			b = lines.find('от ответчиков')
			c = lines.find('от заинтересованного лица')

			# Make this cleaner!!!
			if a > 0:
				if 'не явился' in lines[a:(a+100)] or 'не явились' in lines[a:(a+100)] or 'извещен' in lines[a:(a+100)]:
					self.dappeared = False
				else:
					self.dappeared = True
			elif b > 0:
				if 'не явился' in lines[b:(b+100)] or 'не явились' in lines[b:(b+100)] or 'извещен' in lines[b:(b+100)]:
					self.dappeared = False
				else:
					self.dappeared = True
			elif c > 0:
				if 'не явился' in lines[c:(c+100)] or 'не явились' in lines[c:(c+100)] or 'извещен' in lines[c:(c+100)]:
					self.dappeared = False
				else:
					self.dappeared = True
			elif lines.find('при участии представителя ответчика') > 0:
				self.dappeared = True
			else:
				for phrase in noShow:
					if lines.find(phrase) > 0:
						self.dappeared = False
				self.dappeared = 'Uncertain'

	def pwText(self):
		"""Called if keyword found in pWithdrew function, searches text for string indicating
		that the plaintiff was present at the hearing """
		
		not_withdrew = 'мирового соглашения'
		
		with open(self.txt_name) as searchfile:
			lines = searchfile.read()
			if lines.find(not_withdrew) > 0:
				self.PW = 'No'
			else:
				self.PW = 'Yes'

	def settledText(self):
		"""Called if phrase found by self.settled(), searches for 2 phrases to confirm
		or deny that the case was settled out of court."""

		settled_phrases = [u'мирового соглашения', u'мировое соглашение']

		with open(self.txt_name) as searchfile:
			lines = searchfile.read()
			for phrase in settled_phrases:
				if lines.find(phrase) > 0:
					self.SoC = 'Yes'
					return

		self.SoC = 'No'

	


###############
### Helpers ###
###############

def typeOf(name):
	name = name.replace('"', '').split()
	if name[0].isupper():
		if name[0] == u'ИП' or name[0] == u'НП':
			return 'individual'
		else:
			return name[0]
	else:
		if len(name) >= 3 and (name[2][-3:] == u'вна' or name[2][-3:] == u'вич'):
			return 'individual'
		else:
			return 'gov'

######################
### PDF Operations ###
#####################

def pdf_to_txt(case):
	"""Couldn't figure this bit out so I took code off of stack overflow,
	credit to user tgray"""

    class CsvConverter(TextConverter):
        def __init__(self, *args, **kwargs):
            TextConverter.__init__(self, *args, **kwargs)

        def end_page(self, i):
            from collections import defaultdict
            lines = defaultdict(lambda : {})
            for child in self.cur_item._objs:                #<-- changed
                if isinstance(child, LTChar):
                    (_,_,x,y) = child.bbox                   
                    line = lines[int(-y)]
                    line[x] = child._text.encode(self.codec) #<-- changed

            for y in sorted(lines.keys()):
                line = lines[y]
                self.outfp.write("".join(line[x] for x in sorted(line.keys())))
                self.outfp.write("\n")

    rsrc = PDFResourceManager()
    outfp = StringIO()
    device = CsvConverter(rsrc, outfp, codec="utf-8", laparams=LAParams())

    doc = PDFDocument()
    fp = open(case.pdf_name, 'rb')
    parser = PDFParser(fp)       
    parser.set_document(doc)     
    doc.set_parser(parser)       
    doc.initialize('')

    interpreter = PDFPageInterpreter(rsrc, device)


    for i, page in enumerate(doc.get_pages()):
        outfp.write("START PAGE %d\n" % i)
        if page is not None:
        	interpreter.process_page(page)
        outfp.write("END PAGE %d\n" % i)

    device.close()
    fp.close()

    text_file = open(case.txt_name, "w")
    text_file.write(outfp.getvalue().decode('utf-8').lower().encode('utf-8'))
    text_file.close()

    print('Transfer to .txt complete')



############
### Main ###
############

if __name__ == "__main__":
	driver = webdriver.Firefox()

	tests = ['A40-128070/2011']

	for i, test in enumerate(tests):

		test = case(test)

		if not i:
			test.first_row = True
		else:
			test.first_row = False

		driver.get("http://kad.arbitr.ru/Card?number=" + test.case_id)

		try:
			view_all = driver.find_element_by_xpath('//*[@id="gr_case_partps"]/div/span')
			view_all.click()
		except:
			print('ALL CONTENT DISPLAYED')

		test.web(driver)
		
		pdf_to_txt(test)
		test.text()

		test.data_to_csv()

		os.remove(test.txt_name)

		# REMOVE EVENTUALLY, JGM WANTS PDF COPIES
		# os.remove(test.pdf_name)
		
	driver.close()