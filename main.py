import oauth
from tweepy import API
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import requests
import re
import json, xmltodict

from decimal import *

#grab settings from local file
dtkey = oauth.get_dt_key()
oauth = oauth.getOAuth()


responseAPI = API(oauth)

def extract_number(text):
	r = re.compile('[0-9]+')
	return r.match(text).group()
	pass

def get_book_info(data):
	#get ean from data
	lookupEAN = extract_number(data)
	urlToHit = "http://www.directtextbook.com/xml.php?key=" + dtkey + "&ean=" + lookupEAN
	bookXML = requests.get(urlToHit)
	dictOfXML = xmltodict.parse(bookXML.text)
	items = dictOfXML["book"]["items"]["item"]
	title = dictOfXML["book"]["title"]
	return items, title



def message_generator(vendorList, title):
	messageBP = "Title: {bTitle} The best price overall is {oPrice}, it is {oPType}. Best Price link: {oPLink}. The best new price is {nPrice} @ {nPLink}, the best used price is {uPrice} @ {uPLink}, the best rental price is {rPrice} @ {rPLink}. All best price calculations include shipping."

	#add shipping to price to calculate
	for item in vendorList:
		item['price'] = Decimal(item['price']) + Decimal(item ['shipping'])
		pass

	oLowest = vendorList[0]['price']
	oLowestObj = vendorList[0]
	#calculate overall price
	for item in vendorList:
		if item['price'] < oLowest:
			oLowestObj = item
			oLowest = item['price']
			pass
		pass

	#build type arrays
	newList = []
	usedList = []
	rentalList = []

	for item in vendorList:
		if item['condition'] == "used":
			usedList.append(item)
		if item['condition'] == "new":
			newList.append(item)
		if item['condition'] == "rental":
			rentalList.append(item)

	nLowest = newList[0]['price']
	nLowestObj = newList[0]
	#calculate new price
	for item in newList:
		if item['price'] < nLowest:
			nLowestObj = item
			nLowest = item['price']
			pass
		pass


	uLowest = usedList[0]['price']
	uLowestObj = usedList[0]
	#calculate new price
	for item in usedList:
		if item['price'] < uLowest:
			uLowestObj = item
			uLowest = item['price']
			pass
		pass

	rLowest = rentalList[0]['price']
	rLowestObj = rentalList[0]
	#calculate new price
	for item in rentalList:
		if item['price'] < rLowest:
			rLowestObj = item
			rLowestObj = item['price']
			pass
		pass

	DMText = messageBP.format(oPrice=oLowestObj['price'],oPType=oLowestObj['condition'], oPLink=oLowestObj['url'], nPrice=nLowestObj['price'],  nPLink=nLowestObj['url'],uPrice=uLowestObj['price'], uPLink=uLowestObj['url'],rPrice=rLowestObj['price'], rPLink=rLowestObj['url'], bTitle=title)

	return DMText

	#current
	# for item in vendorList:
	# 	print float(item['price']) + float(item['shipping'])
	# 	print item['condition'], "\n"
	# 	pass
	# pass

class listener(StreamListener):

    def on_direct_message(self, data):
		dataObj = data._json
		EANnum =  dataObj['direct_message']['text']
		requesterId = dataObj['direct_message']['sender_id_str']
		if dataObj['direct_message']['recipient_id_str']== "730138485999304706":
			print requesterId
			print "grabbing book info"
			bookData, bookTitle = get_book_info(EANnum)
			responseDM = message_generator(bookData,bookTitle)
			responseAPI.send_direct_message(user_id=requesterId, text=str(responseDM))
			pass





    def on_error(self, status):
        if status == 401:
            print "make sure VM and host clock are in sync"
        else:
            print status



#get_book_info("9780136006176")



streamInstance = Stream(oauth, listener()) #sets up listener
print "listening"
streamInstance.userstream()
