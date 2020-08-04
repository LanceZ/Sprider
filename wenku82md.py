import os
import sys
import re
import io
import html
import gzip
import urllib
import urllib.request
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar

if len(sys.argv) < 2:
	print('txt2md.py id')
	sys.exit()

id = sys.argv[1]
if len(id) < 4:
	prefix = '0'
else:
	prefix = id[0:1]

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

basedomain = 'www.wenku8.net'
indexUrl = 'https://www.wenku8.net/novel/' + prefix + '/' + id + '/index.htm'
resUrl = 'https://www.wenku8.net/novel/' + prefix + '/' + id + '/'

print('开始处理 ' + id)

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
		print(url)
		output = format(inst)
		print(output)
	return None

def getDocument(url):
	return BeautifulSoup(getResContent(url), 'html.parser')

with open(mdPath, "w", encoding="utf-8") as fo:
	soup = getDocument(indexUrl)

	title = soup.find('div', id='title')
	print(title.text)
	fo.write('\r\n')
	fo.write('<' + title.text + '>\r\n')
	fo.write('\r\n')

	trs = soup.find('table', class_='css').find_all('tr')

	for tr in trs:
		tds = tr.find_all('td')
		for td in tds:
			if td['class'][0] == 'vcss':
				print(td.text)
				fo.write('##' + td.text + '\r\n')
			if td['class'][0] == 'ccss':
				a = td.find('a')
				if a:
					print(td.text + ' ' + a['href'])
					fo.write('###' + td.text)
					soupContent = getDocument(resUrl + a['href'])
					content = soupContent.find('div', id='content')
					
					imgs = soupContent.find_all('img', class_='imagecontent')
					imgnames = []
					for img in imgs:
						imgurl = img['src']
						imgname = os.path.basename(imgurl)
						imgnames.append(imgname)
						if not os.path.exists(imgPath + '/' + imgname):
							opener = urllib.request.build_opener()
							opener.addheaders = [('user-agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')]
							urllib.request.install_opener(opener)
							urllib.request.urlretrieve(imgurl, imgPath + '/' + imgname + '.tmp')
							os.rename(imgPath + '/' + imgname + '.tmp', imgPath + '/' + imgname)
							print('下载图片 ' + imgurl)

					if content.find('ul'):
						[ctag.extract() for ctag in content.find_all('ul')]
					if content.find('div'):
						[ctag.extract() for ctag in content.find_all('div')]
					fo.write(re.sub('\n{3,}', '\n\n', content.text) + '\r\n')

					for iname in imgnames:
						fo.write('\t![avatar](' + iname + ')\r\n')
					if len(imgnames) > 0:
						fo.write('\r\n')
