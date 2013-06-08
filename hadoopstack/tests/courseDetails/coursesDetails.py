import urllib


from config import config
from parser.parser import parser
from parser.makeDict import makeDict

getDetails = lambda year,grade : urllib.urlopen(config.url, urllib.urlencode({'rno':year,'grade':grade,'submit':'submit'})).read()






raw_list=[ getDetails(year,grade) for year in config.years for grade in config.grades ]

for no,i in enumerate(raw_list):
	individualList=parser(i)
	dictionary=makeDict(individualList)
	print dictionary
#print raw_list




