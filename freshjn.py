# -*- coding: utf-8 -*-
#coding = utf-8
import re
import binascii
import time
import urllib
import random
import urllib.request
import html.parser
import requests
import requests.packages.urllib3.util.ssl_
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import gzip
import io
import json
import mysql.connector
import sys
import os

httpheader = {'Accept':'application/json, text/plain, */*', 'Accept-Encoding' : 'gzip, deflate, br', 'Accept-Language' : 'zh-CN,zh;q=0.8', 'Connection' : 'keep-alive', 'Content-Type' : 'application/x-www-form-urlencoded', 'Host' : 'api.freshjn.com', 'Origin' : 'http://m.freshjn.com', 'Referer' : 'http://m.freshjn.com/', 'User-Agent' : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36', 'X-freshjn-Authorization' : ''}

basedomain = 'http://m.freshjn.com'
catUrl = 'https://api.freshjn.com/v2/ecapi.category.list'
listurl = 'https://api.freshjn.com/v2/ecapi.product.list'
prodAjaxUrl = 'https://api.freshjn.com/v2/ecapi.product.get'
timeinterval = 1

def getResContent(url, data):
	try:
		req = urllib.request.Request(url, urllib.parse.urlencode(data).encode('utf-8'), httpheader, method='POST')
		cj = CookieJar()
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		response = opener.open(req)
		bs = response.read()
		response.close()
		#print(bs)

		return bs
	except urllib.request.HTTPError as inst:
		output = format(inst)
		print(output)
	return None

def saveProdImg(data):
	prodJson = json.loads(getResContent(prodAjaxUrl, data).decode('utf-8'))
	#print(prodJson)
	prod = prodJson['product']
	prodImgs = prod['photos']
	
	path = r"d:/Project/sprider/freshjn/prods/" + str(prod['id'])
	try:
		os.makedirs(path)
	except:
		None
	for i in prodImgs:
		p = path + "/" + os.path.basename(i)
		opener = urllib.request.build_opener()
		opener.addheader =  httpheader
		urllib.request.install_opener(opener)
		urllib.request.urlretrieve(i, p)
		print("save prod image success[" + i + "]")
	p = path + "/" + str(prod['id']) + ".json"
	f = open(p, "w")
	f.write(str(prod))
	f.close()
	print("save prod json success[" + str(prod['id']) + "]")

def handleList(cid, listUrl, data):
	listJson = getResContent(listUrl, data).decode('utf-8')
	prodList = json.loads(listJson)

	atitle = prodList['products']

	for a in atitle:
		d = {'product' : a['id'], 'always_send_city':always_send_city}
		saveProdImg(d)

def getCat():
	data = {'page':1,'per_page':100}
	catJson = getResContent(catUrl, data).decode('utf-8')
	catList = json.loads(catJson)
	#print(catList)
	catList = catList['categories']

	categoryList = []

	for pc in catList:
		for c in pc['last_cats']:
			catId = c['cat_id']
			catName = c['cat_name']
			c = [catId, catName]
			categoryList.append(c)

	return	categoryList

always_send_city = 104104101

clist = getCat()

for cid in clist:
	url = listurl
	data = {'page':1,'per_page':100,'keyword':str(cid[1]),'always_send_city':always_send_city}
	handleList(cid, url, data)

print('处理完成')
