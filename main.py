import oauth
from tweepy import API
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import requests
import re
import json, xmltodict


dtkey = oauth.get_dt_key()

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
	jsonResponse = json.dumps(dictOfXML)
	print jsonResponse
	pass


class listener(StreamListener):

    def on_direct_message(self, data):
		dataObj = data._json
		EANnum =  dataObj['direct_message']['text']
		requesterId = dataObj['direct_message']['sender_id_str']
		print requesterId
		bookData = get_book_info(EANnum)


    def on_error(self, status):
        if status == 401:
            print "make sure VM and host clock are in sync"
        else:
            print status


oauth = oauth.getOAuth()

streamInstance = Stream(oauth, listener()) #sets up listener
streamInstance.userstream()
