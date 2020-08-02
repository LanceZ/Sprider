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

if len(sys.argv) < 3:
	print('txt2md.py inputTextFile')
	sys.exit()

inputFile = sys.argv[1]
id = sys.argv[2]
if len(id) < 4:
	prefix = '0'
else:
	prefix = id[0:1]

imgPath = os.path.abspath('.') + '/' + id
if not os.path.exists(imgPath):
	os.makedirs(imgPath)

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
imgIndexUrl = 'https://www.wenku8.net/novel/' + prefix + '/' + id + '/'

print('开始处理 ' + inputFile)

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

def handleImg(line):
	soup = getDocument(indexUrl)

	ret = []

	iiu = imgIndexUrl
	lasthref = ''
	for a in soup.find_all('a', text='插图'):
		title = (a.parent.parent.find_previous('td', class_='vcss'))
		if title.text in line and ' 插图' in line:
			lasthref = a['href']
	iiu += lasthref
	
	soup = getDocument(iiu)
	imgs = soup.find_all('img', class_='imagecontent')
	for img in imgs:
		imgurl = img['src']
		imgname = os.path.basename(imgurl)
		ret.append(imgname)
		if not os.path.exists(imgPath + '/' + imgname):
			urllib.request.urlretrieve(imgurl, imgPath + '/' + imgname)
			print('下载图片 ' + imgurl)

	return ret

if os.path.exists("%s.md" % inputFile):
	os.remove("%s.md" % inputFile)
with open(inputFile, "r", encoding="utf-8") as fi, open("%s.md" % inputFile, "w", encoding="utf-8") as fo:
	for line in fi:
		newline = html.unescape(line)
		newline = re.sub('^.+轻小说文库.+', '', newline)
		newline = re.sub('^[◆|◇]+$', '', newline)
		if not re.match('^<.+>', line):
			newline = re.sub('(^\S+)', lambda x : '###' + x.group(0), newline)
		fo.write(newline)
		if re.match('^###.*插图', newline):
			print('处理插图 ' + line)
			imgs = handleImg(line)
			fo.write('\r\n')
			for img in imgs:
				fo.write('\t![avatar](' + img + ')\r\n')
		
