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
import mysql.connector
import sys

httpheader = {
	':authority':'top.taobao.com',
	':method':'GET',
	':path':'/index.php?spm=a1z5i.1.2.1.Vo5uDt&topId=HOME',
	':scheme':'https',
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'accept-encoding':'gzip, deflate, sdch, br',
	'accept-language':'zh-CN,zh;q=0.8',
	'cookie':'cna=dfKyDFj//0MCAQ4X6UzSx94l; _um_uuid=81cdb81c18c2d123ba84863294665f58; lzstat_uv=21891793552587658154|3492151@3600092@3008922; miid=7009961616301374574; thw=cn; _cc_=W5iHLLyFfA%3D%3D; tg=0; uc3=nk2=&id2=&lg2=; hng=CN%7Czh-cn%7CCHN; tracknick=; v=0; cookie2=1c17cf2f238d287c340930eaaaf7464f; t=041ad95e5f2383e6ceb3966f994d2f81; mt=ci%3D-1_1; l=AsvLHLLntOD/C4J4L41PG6H522W1t98r; isg=AqOjltBK_6uRKbwik3qdLV9QMuH4hjfa4BJ5e9UAKIKwFMI2XWj_Ko4GeFPg',
	'referer':'https://top.taobao.com/index.php?spm=a1z5i.1.2.1.hUTg2J&topId=HOME',
	'upgrade-insecure-requests':'1',
	'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
}

basedomain = 'top.taobao.com'
indexUrl = 'https://top.taobao.com/index.php?spm=a1z5i.1.2.1.hUTg2J&topId=HOME'

jsonBegin = 'g_page_config = '
jsonEnd = 'g_srp_loadCss();'

topType = ['search', 'brand']

user = 'root'
pwd  = '123456'
host = '127.0.0.1'
db   = 'sprider'
charset = 'utf8'

insert_sql = '''INSERT INTO t_taobao_top(sprider_date,cat1,cat2,cat3,top_name,focus,key_word,
	url,num,percent,uod_pos,uod_pos_arrow,uod_percent,uod_percent_arrow) 
	VALUES (%(sprider_date)s,%(cat1)s,%(cat2)s,%(cat3)s,%(top_name)s,%(focus)s,%(key_word)s,
	%(url)s,%(num)s,%(percent)s,%(uod_pos)s,%(uod_pos_arrow)s,%(uod_percent)s,%(uod_percent_arrow)s)'''

delete_sql = '''DELETE FROM t_taobao_top WHERE sprider_date=%(sprider_date)s 
	and cat1=%(cat1)s and cat2=%(cat2)s and cat3=%(cat3)s and top_name=%(top_name)s'''

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

def getJsonData(url):
	soup = getDocument(url)

	allScript = soup.find_all('script')

	for scriptStr in allScript:
		if scriptStr.string:
			#print(scriptStr.string)
			script = scriptStr.string.strip()
			i = script.find(jsonBegin)
			if i >= 0:
				script = script[i + len(jsonBegin) : script.find(jsonEnd)].strip()
				script = script[0 : len(script) - 1]
				#print(script)
				data = json.loads(script)
				return data

def getTabUrls(url):
	data = getJsonData(url)

	tabUrls = []
	for tabData in data['mods']['tab']['data']['tabs']:
		if tabData['id'] != 'HOME':
			url = {'name' : tabData['text'], 'url' : 'https:' + tabData['href']}
			tabUrls.append(url)

	return tabUrls

def getCatUrls(url):
	data = getJsonData(url)

	catUrls = []
	for sub in data['mods']['nav']['data']['common']:
		for catData in sub['sub']:
			url = {'name' : catData['text'], 'parent' : sub['text'], 'url' : 'https://' + basedomain + catData['url']}
			catUrls.append(url)

	return catUrls

def getTopUrls(url):
	data = getJsonData(url)

	topUrls = []
	for topData in data['mods']['bswitch']['data']['switchs']:
		if topData['rank'] in topType:
			url = {'name' : topData['name'], 'url' : 'https://' + basedomain + topData['url']}
			topUrls.append(url)

	return topUrls

def saveTopData(url, cat1, cat2, cat3, topName):
	try:
		data = getJsonData(url)

		sprider_date = time.strftime("%Y%m%d", time.localtime())

		cursor.execute(delete_sql, {'sprider_date' : sprider_date,
				'cat1' : cat1,
				'cat2' : cat2,
				'cat3' : cat3,
				'top_name' : topName})

		for top in data['mods']['wbang']['data']['list']:
			record = {
				'sprider_date' : sprider_date,
				'cat1' : cat1,
				'cat2' : cat2,
				'cat3' : cat3,
				'top_name' : topName,
				'focus' : top['col1']['text'],
				'key_word' : top['col2']['text'],
				'url' : top['col2']['url'],
				'num' : top['col4']['num'],
				'percent' : top['col4']['percent'],
				'uod_pos' : top['col5']['text'],
				'uod_pos_arrow' : top['col5']['upOrDown'],
				'uod_percent' : top['col6']['text'],
				'uod_percent_arrow' : top['col6']['upOrDown']
			}
			cursor.execute(insert_sql, record)

		cnx.commit()
	except:
		print(url)
		print("Unexpected error:", sys.exc_info())
		

cnx = mysql.connector.connect(user=user, password=pwd, host=host, database=db, charset=charset)
cursor = cnx.cursor()

tabUrls = getTabUrls(indexUrl)
for tab in tabUrls:
	catUrls = getCatUrls(tab['url'])
	for cat in catUrls:
		topUrls = getTopUrls(cat['url'])
		for top in topUrls:
			saveTopData(top['url'], tab['name'], cat['parent'], cat['name'], top['name'])
			#print(cat['name'] + tab['name'] + top['name'])
			#print(data)
			#break
		#break
	#break

cursor.close()
cnx.close()


print('处理完成')
