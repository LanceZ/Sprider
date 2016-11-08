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

def getTopUrls(url):
	data = getJsonData(url)

	topUrls = []
	for topData in data['mods']['bswitch']['data']['switchs']:
		if topData['rank'] in topType:
			url = {'name' : topData['name'], 'url' : 'https://' + basedomain + topData['url']}
			topUrls.append(url)

	return topUrls

def getTopData(url):
	#print(url)
	data = getJsonData(url)

	topList = []
	for top in data['mods']['wbang']['data']['list']:
		record = {
			'focus' : top['col1']['text'],
			'keyWord' : top['col2']['text'],
			'url': top['col2']['url'],
			'num': top['col4']['num'],
			'percent': top['col4']['percent'],
			'upOrDownPos': top['col5']['text'],
			'upOrDownPosArrow': top['col5']['upOrDown'],
			'upOrDownPercent': top['col6']['text'],
			'upOrDownPercentArrow': top['col6']['upOrDown']
		}
		#print(record)
		topList.append(record)
		#break
	return topList

tabUrls = getTabUrls(indexUrl)
for tab in tabUrls:
	topUrls = getTopUrls(tab['url'])
	for top in topUrls:
		data = getTopData(top['url'])
		print(tab['name'] + top['name'])
		#print(data)
		#break
	break
