from bs4 import BeautifulSoup
#from config import makedict
from itertools import *

def parser(raw_list):
		soup = BeautifulSoup(raw_list)
		tags=soup.findAll('td')
		textAll=[ i.text.replace(u'\xa0', u' ').encode('ascii').split('   ') for i in tags ]
		itex=iter(textAll)
		individualList=[ i   for i in izip(itex,itex,itex)]
		return individualList


			

