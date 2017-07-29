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
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import gzip
import io
import json
import pymysql.cursors
import sys

httpheader = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Encoding':'gzip, deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8', 'Cache-Control':'max-age=0', 'Connection':'keep-alive', 'Cookie':'davisit=14; usertrack=3/zPBVgQTXyikQ3gAwuQAg==; JSESSIONID-WKL-8IO=8xOepyQWlEuXyZfCTu65UGIjKd%2BbBbrUiirW2398NuCRhgPh%2FrkaGm%5CHtkt5neB0ZXit3Z%5CGt%2FPMRrOnfCbm%2BggcJSYtkPouqhA9nhVwR4Wu5ELpwKCHgKkjs9eBNA10xV5N32mlAHxM4tKx4xe07tm8VKUQ012lVuHeZIGcVEKLhDq%2B%3A1477549805588; _klhtxd_=31; KAOLA_NEW_USER_COOKIE=no; HTONLINE=c7acb8995375bf157943033bfc44aa84e8d6909e; _ntes_nnid=6b00fdd64addf0eb9b6082117d57a049,1477463406261; davisit=1; __da_ntes_utmfc=utmcsr%3D(direct)%7Cutmccn%3D(direct)%7Cutmcmd%3D(none); __kaola_usertrack=20161026143246618886; _da_ntes_uid=20161026143246618886; __nteskl_xk=1477470497842; NTES_KAOLA_NEW_CUST=1; NTES_KAOLA_RV=1299241_1477470497884_0%7C32178_1462335258910_0; NTESwebSI=601B66249B4EA89965A854A584511EBA.hzabj-haitao-web5.server.163.org-8010; _ntes_nuid=6b084a11f79d2b0668ebfd606d93fa10; SHIPPING_TO_CITY_CODE_NEW=440100; _dc_gtm_UA-60320154-1=1; _pzfxuvpc=1477463406437%7C4211452708121409958%7C7%7C1477471849616%7C3%7C7662468003821827363%7C1121463776128479421; _pzfxsvpc=1121463776128479421%7C1477470498173%7C4%7C; __utma=243297311.1857333332.1477463407.1477467244.1477470498.3; __utmb=243297311.4.10.1477470498; __utmc=243297311; __utmz=243297311.1477463407.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __da_ntes_utma=2525167.729642695.1477463407.1477463550.1477470499.3; __da_ntes_utmb=2525167.7.10.1477470499; __da_ntes_utmz=2525167.1477463407.1.1.utmcsr%3D(direct)%7Cutmccn%3D(direct)%7Cutmcmd%3D(none); Hm_lvt_645b0165bab4840cd77ab93b4bc41821=1477463407; Hm_lpvt_645b0165bab4840cd77ab93b4bc41821=1477471851; _ga=GA1.2.1857333332.1477463407', 'Host':'www.kaola.com',  'Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'}

basedomain = 'http://www.kaola.com'
catUrl = 'http://www.kaola.com/getFrontCategory.shtml'
listurl = 'http://www.kaola.com/category/#id#.html'
prodAjaxUrl = 'http://www.kaola.com/recentlyViewAjax.html?id='
prodPriceUrl = 'http://www.kaola.com/product/ajax/queryPromotionTitle.html?goodsId='
timeinterval = 1

user = 'root'
pwd  = '123456'
host = '127.0.0.1'
db   = 'sprider'
charset = 'utf8'

insert_sql = '''INSERT INTO t_product(webdomain, prod_id, cat_id, cat_name, prod_name, prod_price, 
	prod_price_app, prod_imgs, brand_name, comment_count, orig_country, discount, favorite_count, prod_props, 
	tax_rate, market_price, member_count, member_price, member_price_app, suggest_price, warehouse_city) 
	VALUES (%(webdomain)s,%(prod_id)s,%(cat_id)s,%(cat_name)s,%(prod_name)s,%(prod_price)s,%(prod_price_app)s,
	%(prod_imgs)s,%(brand_name)s,%(comment_count)s,%(orig_country)s,%(discount)s,%(favorite_count)s,%(prod_props)s,
	%(tax_rate)s,%(market_price)s,%(member_count)s,%(member_price)s,%(member_price_app)s,%(suggest_price)s,%(warehouse_city)s)'''

update_sql = '''update t_product set cat_id=%(cat_id)s, cat_name=%(cat_name)s, prod_name=%(prod_name)s, prod_price=%(prod_price)s, 
	prod_price_app=%(prod_price_app)s, prod_imgs=%(prod_imgs)s, brand_name=%(brand_name)s, comment_count=%(comment_count)s, 
	orig_country=%(orig_country)s, discount=%(discount)s, favorite_count=%(favorite_count)s, prod_props=%(prod_props)s, 
	tax_rate=%(tax_rate)s, market_price=%(market_price)s, member_count=%(member_count)s, member_price=%(member_price)s, 
	member_price_app=%(member_price_app)s, suggest_price=%(suggest_price)s, warehouse_city=%(warehouse_city)s 
	where webdomain=%(webdomain)s and prod_id=%(prod_id)s'''

select_sql = "SELECT count(1) prodCount FROM t_product where webdomain=%(webdomain)s and prod_id=%(prod_id)s"

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

def handleList(cid, listUrl):
	soup = getDocument(listUrl)

	atitle = soup.find_all('a', class_='title')

	print(listUrl + '\t' + str(len(atitle)))

	for a in atitle:
		htmlUrl = a.get('href')
		ajaxUrl = prodAjaxUrl + htmlUrl.replace('/product/', '').replace('.html', '')
		saveProd(cid, ajaxUrl, basedomain + htmlUrl)
	
	nexta = soup.find_all('a', class_='nextPage')
	if nexta:
		nexturl = basedomain + nexta[0].get('href')
		#print(nexturl)
		handleList(cid, nexturl)

def saveProd(cid, ajaxUrl, htmlUrl):
	try:
		pordJson = getResContent(ajaxUrl).decode('utf-8')
		prod = json.loads(pordJson)
		
		record = {}
		if prod['list'] and prod['list'][0]:
			record = getProdObjByAjax(cid, prod['list'][0])
		else:
			record = getProdObjByHtml(cid, getDocument(htmlUrl))

		cursor.execute(select_sql, record)

		operType = ''

		result = cursor.fetchone()
		if (result['prodCount'] <= 0):
			cursor.execute(insert_sql, record)
			operType = '插入'
		else:
			cursor.execute(update_sql, record)
			operType = '更新'

		cnx.commit()
		#print(ajaxUrl + operType + '成功')

	except:
		print(ajaxUrl)
		print("Unexpected error:", sys.exc_info())

def getProdObjByHtml(cid, soup):
	prodId = soup.find(id='goodsId')['value']
	prodName = soup.find(class_='crumbs-title').string
	origCountry = soup.find(class_='orig-country').find('span').string
	brandName = soup.find(class_='orig-country').find('a').string

	prodImgList = 'None'

	commentCount = 'None'
	favoriteCount = 'None'

	priceJson = getResContent(prodPriceUrl + prodId).decode('utf-8')
	priceObj = json.loads(priceJson)
	prodPrice = priceObj['data']['currentPrice']
	prodPriceApp = 'None'
	marketPrice = priceObj['data']['marketPrice']
	memberCount = priceObj['data']['memberCount']
	memberPrice = priceObj['data']['memberPrice']
	memberPriceForApp = 'None'
	discount = 'None'
	taxRate = 'None'
	suggestPrice = priceObj['data']['suggestPrice']
	warehouseCityShow = soup.find(class_='postage').find(class_='from').string

	prodProp = []
	prodAttrLi = soup.find(class_='goods_parameter').find_all('li')
	for p in prodAttrLi:
		attr = p.string
		attr = attr.split('：')
		attrObj = {attr[0] : attr[1]}
		prodProp.append(attrObj)

	record = {
		'webdomain' : basedomain, 
		'prod_id' : str(prodId), 
		'cat_id' : str(cid[0]),
		'cat_name' : str(cid[1]), 
		'prod_name' : str(prodName), 
		'prod_price' : str(prodPrice), 
		'prod_price_app' : str(prodPriceApp), 
		'prod_imgs' : str(prodImgList), 
		'brand_name' : str(brandName), 
		'comment_count' : str(commentCount), 
		'orig_country' : str(origCountry), 
		'discount' : str(discount), 
		'favorite_count' : str(favoriteCount), 
		'prod_props' : str(prodProp), 
		'tax_rate' : str(taxRate), 
		'market_price' : str(marketPrice), 
		'member_count' : str(memberCount), 
		'member_price' : str(memberPrice), 
		'member_price_app' : str(memberPriceForApp), 
		'suggest_price' : str(suggestPrice), 
		'warehouse_city' : str(warehouseCityShow)
	}
	return record

def getProdObjByAjax(cid, prod):
	prodId = prod['goodsId']
	prodName = prod['title']
	prodPrice = prod['actualCurrentPrice']
	prodPriceApp = prod['actualCurrentPriceForApp']
	prodImgList = prod['imageUrlList']
	brandName = prod['brandName']
	commentCount = prod['commentCount']
	origCountry = prod['originCountryName']
	discount = prod['discount']
	favoriteCount = prod['favoriteCount']
	prodProp = []
	for prop in prod['goodsPropertyList']:
		propName = prop['propertyNameCn']
		propValue = ''
		for propV in prop['propertyValues']:
			propValue = propValue + " " + propV['propertyValue']
		prodProp.append({propName : propValue})
	taxRate = prod['internetComposeTaxRate']
	marketPrice = prod['marketPrice']
	memberCount = prod['memberCount']
	memberPrice = prod['memberPrice']
	memberPriceForApp = prod['memberPriceForApp']
	suggestPrice = prod['suggestPrice']
	warehouseCityShow = prod['warehouseCityShow']

	record = {
		'webdomain' : basedomain, 
		'prod_id' : str(prodId), 
		'cat_id' : str(cid[0]),
		'cat_name' : str(cid[1]), 
		'prod_name' : prodName, 
		'prod_price' : str(prodPrice), 
		'prod_price_app' : str(prodPriceApp), 
		'prod_imgs' : str(prodImgList), 
		'brand_name' : brandName, 
		'comment_count' : str(commentCount), 
		'orig_country' : origCountry, 
		'discount' : str(discount), 
		'favorite_count' : str(favoriteCount), 
		'prod_props' : str(prodProp), 
		'tax_rate' : str(taxRate), 
		'market_price' : str(marketPrice), 
		'member_count' : str(memberCount), 
		'member_price' : str(memberPrice), 
		'member_price_app' : str(memberPriceForApp), 
		'suggest_price' : str(suggestPrice), 
		'warehouse_city' : str(warehouseCityShow)
	}
	return record

def getCat():
	catJson = getResContent(catUrl).decode('utf-8')
	catList = json.loads(catJson)
	catList = catList['frontCategoryList']

	categoryList = []

	for pc in catList:
		for c in pc['childrenNodeList']:
			catId = c['categoryId']
			catName = c['categoryName']
			c = [catId, catName]
			categoryList.append(c)

	return	categoryList

cnx = pymysql.connect(user=user, password=pwd, host=host, db=db, charset=charset, cursorclass=pymysql.cursors.DictCursor)
cursor = cnx.cursor()

clist = getCat()
#print(str(clist))

for cid in clist:
	url = listurl.replace('#id#', str(cid[0]))
	handleList(cid, url)

cursor.close()
cnx.close()

print('处理完成')
