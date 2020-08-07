"""
P1sty is a python Tool that allows you to generate fully coded P1sty spiders
for any given paste website in less than a second.

P1sty's spiders allows you to monitor a given paste website for occurrence of
 your business name, domain, emails, credentials, Credit cards, etc.

Once the fraudulent information is detected, you will be notified in real time
by e-mail, and a MISP event will be automatically created.

Then you should verify the certainty of the alert, if it is true positive,
you should inform Fraud departement and notify your MISP community.


MIT License

Copyright (c) 2020 Abdelkader BEN ALI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



import argparse
import os
import sys
import textwrap
from termcolor import colored
from urlparse import urlparse

import smtplib


def banner():
	banner = """ 
  _____  __     _         
 |  __ \/_ |   | |        
 | |__) || |___| |_ _   _ 
 |  ___/ | / __| __| | | |
 | |     | \__ \ |_| |_| |
 |_|     |_|___/\__|\__, |
                     __/ |
                    |___/ 
"""
	by = """
===> developed by Abdelkader BEN ALI

"""
	print colored(banner,'green')
	print colored(by,'red')

def generate():
	banner()
	parser = argparse.ArgumentParser(description='P1sty allows you to generate fully coded P1sty spiders that monitors a given paste website looking for any kind of information that can be used to commit fraud against you organization')
	parser.add_argument("-n","--name", required=True, type=str, help="Spider name")
	parser.add_argument("-s","--start", required=True, type=str, help="Archive url")
	parser.add_argument("-m","--misp", required=True, type=str, help="Misp events url")
	parser.add_argument("-k","--key", required=True, type=str, help="Misp key")
	parser.add_argument("-lpx", required=True, type=str, help="Latest pastes XPath")
	parser.add_argument("-rpx", required=True, type=str, help="Raw paste data XPath")
	parser.add_argument("-ux", required=True, type=str, help="Username XPath")
	parser.add_argument("-d","--domain", default="",type=str, help="Company domain")
	parser.add_argument("-b","--bin", default="",type=str, help="Company BIN")
	parser.add_argument("-se","--sender", default="",type=str, help="Sender email address")
	parser.add_argument("-p","--password", default="",type=str, help="Sender email password")
	parser.add_argument("-r","--recipient", default="",type=str, help="Recipient email")
	args = parser.parse_args()

	name = args.name
	start_urls = args.start
	allowed_domains = urlparse(start_urls).netloc
	misp_url = args.misp
	misp_key = args.key
	latest_pastes_ids_xpath = args.lpx
	raw_paste_data_xpath = args.rpx
	username_xpath = args.ux
	company_domain = args.domain
	company_bin = args.bin
	sender_email = args.sender
	sender_password = args.password
	recipient_email = args.recipient

	if not company_domain and not company_bin:
		print colored('[!] You need at least to specify either your company domain or your BIN','red')
		sys.exit(0)

	if company_domain:
		domain_regex = company_domain
		email_regex = "(?i)[a-zA-Z0-9._-]+@" + company_domain
		credential_regex = "(?i)[a-zA-Z0-9._-]+@" + company_domain + ":[a-z0-9\_\-*]+"
	else:
		domain_regex = ""
		email_regex = ""
		credential_regex = ""

	if company_bin:
		first_four_digits = company_bin[:4]
		sencond_two_digits = company_bin[4:]
		cc_regex = r"\b(%s[ -]?%s\d{2}[ -]?\d{4}[ -]?\d{4})\b"%(first_four_digits,sencond_two_digits)
	else:
		cc_regex = ""

	if sender_email:
		if sender_password and recipient_email:
			if not verify_email_password(sender_email,sender_password):
				print colored('[!] Email address or password is incorrect','red')
				sys.exit(0)
		else:
			print colored('[!] If you want to receive email notification you need to specify both recipient email and password','red')
			sys.exit(0)


	data1 = '''\
	import scrapy
	import re
	import requests
	import json
	import time
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	import smtplib, ssl
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	class Pasty(scrapy.Spider):
		name = '%s'
		allowed_domains = ['%s']
		start_urls = ['%s']
		visited_pastes = []
		btc_regex = r"[13][a-km-zA-HJ-NP-Z1-9]{25,34}"
		misp_url = "%s"
		misp_key = "%s"
		domain_regex = "%s"
		email_regex = "%s"
		credential_regex = "%s"
		cc_regex = r"%s"
		sender_email = "%s"
		sender_password = "%s"
		recipient_email = "%s"

		def parse(self, response):
			latest = self.latest_pastes(response)
			for link in latest:
				if link not in self.visited_pastes:
					yield response.follow(link, self.parse_paste)
			time.sleep(3)
			yield scrapy.Request(self.start_urls[0],callback=self.parse,dont_filter=True)

		def latest_pastes(self,response):
			latest_pastes_ids = response.xpath("%s").getall()
			return latest_pastes_ids

		def parse_paste(self,response):
			paste_link = response.url
			raw_paste_data = response.xpath("normalize-space(%s)").get().encode("utf-8")
			raw_paste_data = raw_paste_data.replace("'","")
			username = response.xpath("normalize-space(%s)").get().encode("utf-8")
			self.visited_pastes.append(paste_link)
			btc = re.findall(self.btc_regex, raw_paste_data)
			if self.domain_regex:
				credentials = re.findall(self.credential_regex, raw_paste_data)
				if credentials:
					print("credentials were found")
					self.misp_create_event(paste_link, raw_paste_data, username, credentials, btc, "creds")
				else:
					emails = re.findall(self.email_regex, raw_paste_data)
					if emails:
						print('emails were found')
						self.misp_create_event(paste_link, raw_paste_data, username, emails, btc, "emails")
					else:
						domain_occ = re.findall(self.domain_regex, raw_paste_data)
						if domain_occ:
							self.misp_create_event(paste_link, raw_paste_data, username, domain_occ, btc, "domain")
			if self.cc_regex:
				cc_list = re.findall(self.cc_regex, raw_paste_data)
				if cc_list:
					print("cards were found")
					self.misp_create_event(paste_link, raw_paste_data, username, cc_list, btc, "cc")
				'''
	data1 = data1%(name, allowed_domains, start_urls, misp_url, misp_key, domain_regex, email_regex, credential_regex, cc_regex, sender_email, sender_password, recipient_email, latest_pastes_ids_xpath, raw_paste_data_xpath, username_xpath)
	data2 = '''\n

		def emails_attribute(self, emails):
			attributes = []
			for email in emails:
				attributes.append({"type":"text","category":"Other","distribution":"0","comment":"","value":email})
			return attributes

		def cc_attribute(self, cc_list):
			attributes = []
			for ccn in cc_list:
				attributes.append({"type":"cc-number","category":"Financial fraud","distribution":"0","comment":"","value":ccn})
			return attributes

		def send_email_notification(self, sender_email, sender_password, recipient_email, subject, body):
			mail_content = """
			Dear Team,

			%s

			Regards,
			P1sty
			"""%(body)
			message = MIMEMultipart()
			message['From'] = sender_email
			message['To'] = recipient_email
			message['Subject'] = subject
			message.attach(MIMEText(mail_content, 'plain'))
			session = smtplib.SMTP('smtp.gmail.com', 587) 
			session.starttls()
			try:
				session.login(sender_email, sender_password) 
				text = message.as_string()
				session.sendmail(sender_email, recipient_email, text)
				session.quit()
				print('Mail Sent')
			except smtplib.SMTPAuthenticationError:
				print('Failed to send the email')


		def misp_create_event(self, link, raw_data, username, data_found, btc, data_type):
			headers = {'Authorization': '%s'%(self.misp_key), 'Accept': 'application/json', 'Content-type': 'application/json',}
			attributes = []
			username_attribute = {"type":"text","category":"Other","distribution":"0","comment":"","value":username}
			attributes.append(username_attribute)
			link_attribute = {"type":"text","category":"Other","disable_correlation":"yes", "distribution":"0" ,"comment":"" ,"value": link}
			attributes.append(link_attribute)
			raw_data_attribute = {"type":"text","category":"Other","disable_correlation":"yes","distribution":"0","comment":"","value": raw_data}
			attributes.append(raw_data_attribute)
			if data_type == "creds":
				creds = data_found
				count = len(creds)
				event_name = str(count)+ " creds found in " + self.allowed_domains[0]
				emails = [cred.split(':')[0] for cred in creds]
				emails_attributes = self.emails_attribute(emails)
				attributes.extend(emails_attributes)
			elif data_type == "emails":
				emails = data_found
				count = len(emails)
				event_name = str(count)+ " emails found in " + self.allowed_domains[0]
				emails_attributes = self.emails_attribute(emails)
				attributes.extend(emails_attributes)
			elif data_type == "domain":
				event_name = "company domain found in " + self.allowed_domains[0]
			else:
				cc_list = data_found
				cc_list = list(set([ccn.replace(" ","").replace("-","") for ccn in cc_list]))
				count = len(cc_list)
				event_name = str(count)+ " credit card numbers found in " + self.allowed_domains[0]
				cc_attributes = self.cc_attribute(cc_list)
				attributes.extend(cc_attributes)
			if btc:
				btc_attribute = {"type":"btc","category":"Financial fraud","distribution":"0","comment":"","value": btc[0]}
				attributes = attributes.append(btc_attribute)
			date = time.strftime("%Y-%m-%d")
			data = '{"Event":{"date":"%s","threat_level_id":"1","info":"%s","published":false,"analysis":"0","distribution":"0","Attribute":%s}}'%(date,event_name,attributes)
			data = data.replace("\'",'"').replace("\\t"," ")
			print(data)
			response = requests.post(self.misp_url, headers=headers, data=data, verify=False)
			event_id = response.json()['Event']['id']
			event_url = self.misp_url + "/" + event_id
			if self.sender_email:
				body = "Please check MISP event: " + event_url
				self.send_email_notification(self.sender_email, self.sender_password, self.recipient_email, event_name, body)
			'''
	data = data1 + data2
	filename = name+".py"
	generate_spider(filename, data)

def generate_spider(filename, data):
	filepath = os.getcwd() + "/P1sty/spiders/"
	full_path = filepath + filename
	with open(full_path, 'w') as f:
		f.write(textwrap.dedent(data))
	print 'Successfully genrated :)'

def verify_email_password(email,password):
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    try:
        response = session.login(email, password)
        return True
    except smtplib.SMTPAuthenticationError:
        return False

if __name__ == "__main__":
    generate()
