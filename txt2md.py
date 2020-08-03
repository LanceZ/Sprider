import os
import sys
import re
import io
import html
import gzip
import urllib
import urllib.request
import brotli
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar

if len(sys.argv) < 2:
	print('txt2md.py id')
	sys.exit()

id = sys.argv[1]

imgPath = os.path.abspath('.') + '/' + id
if not os.path.exists(imgPath):
	os.makedirs(imgPath)

mdPath = id + '.md'
if os.path.exists(mdPath):
	os.remove(mdPath)

httpheader = {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'accept-encoding':'gzip, deflate, sdch, br',
	'accept-language':'zh-CN,zh;q=0.8',
	'cookie':'cna=dfKyDFj//0MCAQ4X6UzSx94l; _um_uuid=81cdb81c18c2d123ba84863294665f58; lzstat_uv=21891793552587658154|3492151@3600092@3008922; miid=7009961616301374574; thw=cn; _cc_=W5iHLLyFfA%3D%3D; tg=0; uc3=nk2=&id2=&lg2=; hng=CN%7Czh-cn%7CCHN; tracknick=; v=0; cookie2=1c17cf2f238d287c340930eaaaf7464f; t=041ad95e5f2383e6ceb3966f994d2f81; mt=ci%3D-1_1; l=AsvLHLLntOD/C4J4L41PG6H522W1t98r; isg=AqOjltBK_6uRKbwik3qdLV9QMuH4hjfa4BJ5e9UAKIKwFMI2XWj_Ko4GeFPg',
	'referer':'https://top.taobao.com/index.php?spm=a1z5i.1.2.1.hUTg2J&topId=HOME',
	'upgrade-insecure-requests':'1',
	'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
}

basedomain = 'www.linovelib.com'
indexUrl = 'https://www.linovelib.com/novel/' + id + '/catalog'
resUrl = 'https://www.linovelib.com/'

print('开始处理 ' + id)

def getResContent(url):
	try:
		req = urllib.request.Request(url, None, httpheader)
		cj = CookieJar()
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		response = opener.open(req)
		bs = response.read()
		bi = io.BytesIO(bs)
		raw_response = brotli.decompress(bs).decode('utf-8')
		response.close()
		#print(raw_response)

		return raw_response
	except urllib.request.HTTPError as inst:
		print(url)
		output = format(inst)
		print(output)
	return None

def getDocument(url):
	return BeautifulSoup(getResContent(url), 'html.parser')

def loadContent(url, page, origUrl):
	soupContent = getDocument(url)
	content = soupContent.find('div', id='TextContent')
	if not content:
		return
	hasNext = False
	for ctag in content.find_all():
		if ctag.name == 'p':
			text = ctag.text
			if '（本章未完）' in text:
				hasNext = True
			fo.write('    ' + text +  '\r\n\r\n')
		if ctag.name == 'div' and ctag['class'][0] == 'divimage':
			img = ctag.find('img', class_='imagecontent')
			imgurl = img['src']
			imgname = os.path.basename(imgurl)
			if not os.path.exists(imgPath + '/' + imgname):
				urllib.request.urlretrieve(imgurl, imgPath + '/' + imgname + '.tmp')
				os.rename(imgPath + '/' + imgname + '.tmp', imgPath + '/' + imgname)
				#print('下载图片 ' + imgurl)
			fo.write('\t![avatar](' + imgname + ')\r\n\r\n')
	if hasNext:
		page += 1
		#print(origUrl + '?page=' + str(page))
		loadContent(origUrl + '?page=' + str(page), page, origUrl)

with open(mdPath, "w", encoding="utf-8") as fo:
	soup = getDocument(indexUrl)

	title = soup.find('div', class_='book-meta').find('h1')
	print(title.text)
	fo.write('\r\n')
	fo.write('<' + title.text + '>\r\n')
	fo.write('\r\n')

	ul = soup.find('ul', class_='chapter-list').find_all(['div', 'a'])
	lastUrl = ''
	firstC = False
	for i, tag in enumerate(ul):
		if tag.name == 'div' and tag['class'][0] == 'volume':
			print(tag.text)
			fo.write('##' + tag.text + '\r\n')
			firstC = True
		if tag.name == 'a':
			a = tag
			#print(a.text + ' ' + a['href'])
			fo.write('###' + a.text + '\r\n')
			ahref = a['href']
			if 'javascript' in ahref:
				print(a.text + ' 缺章')
				if firstC:
					nextUrl = ul[i+1]['href']
					print('下一章' + nextUrl)
					n = int(os.path.basename(nextUrl).split('.')[0])
					ahref = nextUrl.replace(str(n), str(n - 1))
					print('调整为' + ahref)
				else:
					print('上一章' + lastUrl)
					n = int(os.path.basename(lastUrl).split('.')[0])
					ahref = lastUrl.replace(str(n), str(n + 1))
					print('调整为' + ahref)
			loadContent(resUrl + ahref, 1, resUrl + ahref)
			lastUrl = ahref
			firstC = False
