# -*- coding: utf-8 -*-
import re
import binascii
import time
import urllib
import random
import urllib.request
import html.parser
import requests
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import gzip
import io
import json

httpheader = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding':'gzip, deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8', 'Cache-Control':'max-age=0', 'Connection':'keep-alive', 'Cookie':'davisit=14; usertrack=3/zPBVgQTXyikQ3gAwuQAg==; JSESSIONID-WKL-8IO=8xOepyQWlEuXyZfCTu65UGIjKd%2BbBbrUiirW2398NuCRhgPh%2FrkaGm%5CHtkt5neB0ZXit3Z%5CGt%2FPMRrOnfCbm%2BggcJSYtkPouqhA9nhVwR4Wu5ELpwKCHgKkjs9eBNA10xV5N32mlAHxM4tKx4xe07tm8VKUQ012lVuHeZIGcVEKLhDq%2B%3A1477549805588; _klhtxd_=31; KAOLA_NEW_USER_COOKIE=no; HTONLINE=c7acb8995375bf157943033bfc44aa84e8d6909e; _ntes_nnid=6b00fdd64addf0eb9b6082117d57a049,1477463406261; davisit=1; __da_ntes_utmfc=utmcsr%3D(direct)%7Cutmccn%3D(direct)%7Cutmcmd%3D(none); __kaola_usertrack=20161026143246618886; _da_ntes_uid=20161026143246618886; __nteskl_xk=1477470497842; NTES_KAOLA_NEW_CUST=1; NTES_KAOLA_RV=1299241_1477470497884_0%7C32178_1462335258910_0; NTESwebSI=601B66249B4EA89965A854A584511EBA.hzabj-haitao-web5.server.163.org-8010; _ntes_nuid=6b084a11f79d2b0668ebfd606d93fa10; SHIPPING_TO_CITY_CODE_NEW=440100; _dc_gtm_UA-60320154-1=1; _pzfxuvpc=1477463406437%7C4211452708121409958%7C7%7C1477471849616%7C3%7C7662468003821827363%7C1121463776128479421; _pzfxsvpc=1121463776128479421%7C1477470498173%7C4%7C; __utma=243297311.1857333332.1477463407.1477467244.1477470498.3; __utmb=243297311.4.10.1477470498; __utmc=243297311; __utmz=243297311.1477463407.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __da_ntes_utma=2525167.729642695.1477463407.1477463550.1477470499.3; __da_ntes_utmb=2525167.7.10.1477470499; __da_ntes_utmz=2525167.1477463407.1.1.utmcsr%3D(direct)%7Cutmccn%3D(direct)%7Cutmcmd%3D(none); Hm_lvt_645b0165bab4840cd77ab93b4bc41821=1477463407; Hm_lpvt_645b0165bab4840cd77ab93b4bc41821=1477471851; _ga=GA1.2.1857333332.1477463407', 'Host':'www.kaola.com',  'Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'}

basedomain = 'http://www.kaola.com'
listid = ['2620', '2631', '2621', '2664', '2665', '2667']
listurl = 'http://www.kaola.com/category/#id#.html'
prodPriceUrl = 'http://www.kaola.com/product/ajax/queryPromotionTitle.html?goodsId='
timeinterval = 1

def getResContent(url):
	try:
		req = urllib.request.Request(url, None, httpheader)
		cj = CookieJar()
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		response = opener.open(req)
		bs = response.read()
		bi = io.BytesIO(bs)
		raw_response = gzip.GzipFile(fileobj=bi, mode="rb").read()
		response.close()
		#print(raw_response)

		return raw_response
	except urllib.request.HTTPError as inst:
		output = format(inst)
		print(output)
	return None

def getDocument(url):
	return BeautifulSoup(getResContent(url), 'html.parser')

def handleList(listUrl):
	soup = getDocument(listUrl)

	atitle = soup.find_all('a', class_='title')

	for a in atitle:
		prodhref = basedomain + a.get('href')
		saveProd(prodhref)
		#print(prodhref)
		break
	return
	
	nexta = soup.find_all('a', class_='nextPage')
	if nexta:
		nexturl = basedomain + nexta[0].get('href')
		#print(nexturl)
		handleList(nexturl)

def saveProd(url):
	soup = getDocument(url)
	
	prodId = soup.find(id='goodsId')['value']
	prodName = soup.find(class_='crumbs-title').string
	
	priceJson = getResContent(prodPriceUrl + prodId).decode('utf-8')
	priceObj = json.loads(priceJson)
	#print(priceObj)
	prodPrice = priceObj['data']['currentPrice']
	marketPrice = priceObj['data']['marketPrice']

	prodAttr = []
	prodAttrLi = soup.find(class_='goods_parameter').find_all('li')
	for p in prodAttrLi:
		attr = p.string
		attr = attr.split('：')
		prodAttr.append(attr)

	print(prodId + '\t' + prodName + '\t' + str(prodPrice) + '\t' + str(marketPrice) + '\t')

for id in listid:
	url = listurl.replace('#id#', id)
	handleList(url)
