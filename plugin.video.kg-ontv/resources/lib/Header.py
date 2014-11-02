#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, sys, os, base64, urlparse, socket, random, time, hashlib, json
from urllib import urlencode, unquote, quote, quote_plus
from cookielib import CookieJar
import xbmcplugin, xbmcgui, xbmcaddon, xbmc, xbmcaddon

xbmc_version       = xbmc.getInfoLabel('System.BuildVersion')
xbmc_OS            = os.environ.get( 'OS', '' ).lower().replace( 'xbox', "XBox" ).replace( 'win32', 'Windows' ).replace( 'linux', 'GNU/Linux' ).replace( 'osx', 'Mac OS X' )
if not xbmc_OS: xbmc_OS = 'Unknown OS'

__addon__          = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
__language__       = __addon__.getLocalizedString

addon_icon         = __addon__.getAddonInfo('icon')
addon_fanart       = __addon__.getAddonInfo('fanart')
addon_path         = __addon__.getAddonInfo('path')
addon_type         = __addon__.getAddonInfo('type')
addon_id           = __addon__.getAddonInfo('id')
addon_author       = __addon__.getAddonInfo('author')
addon_name         = __addon__.getAddonInfo('name')
addon_version      = __addon__.getAddonInfo('version')
addon_imgpath      = os.path.join(addon_path, 'resources', 'media')
connection_timeout = __addon__.getSetting('connection_timeout')
cache_timeout      = __addon__.getSetting('cache_timeout')
try:
	socket.setdefaulttimeout(int(connection_timeout))
except:
	__addon__.setSetting('connection_timeout', '5')
#socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:    cache_timeout = int(cache_timeout)
except: cache_timeout = 4
if(cache_timeout == 0):
	cache_timeout = 4

UserAgents = ['|User-Agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
		'|User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36',
		'|User-Agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
		'|User-Agent=Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
		'|User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
		'|User-Agent=Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		'|User-Agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14',
		'|User-Agent=Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
		'|User-Agent=Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
		'|User-Agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; chromeframe/12.0.742.112)',
		'|User-Agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.1; SV1; .NET CLR 2.8.52393; WOW64; en-US)',
		'|User-Agent=Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)']
UserAgent = UserAgents[random.randrange(0,len(UserAgents)-1,1)]

MAX_DELAY = 3600*cache_timeout
import sqlite3 as db
db_name = os.path.join(addon_path, 'requests.db')
c = db.connect(database=db_name)
cu = c.cursor()

def add_to_db(n, item):
	err=0
	m = hashlib.md5()
	m.update(str(n))
	req=m.hexdigest()
	data=quote(item)
	try:
		cu.execute("DELETE FROM cache WHERE time < %s" % int(time.time())-MAX_DELAY)
		c.commit()
		xbmc.log('KG OnTV: Кэш очищен')
	except: pass

	try:
		cu.execute("INSERT INTO cache VALUES ('%s','%s','%s')"%(req,data,int(time.time())))
		c.commit()
	except:
		cu.execute("CREATE TABLE cache (link, data, time int)")
		c.commit()
		cu.execute("INSERT INTO cache VALUES ('%s','%s','%s')"%(req,data,int(time.time())))
		c.commit()

def get_inf_db(n):
	m = hashlib.md5()
	m.update(str(n))
	req=m.hexdigest()
	cu.execute("SELECT time FROM cache WHERE link = '%s'" % req)
	c.commit()
	tout = cu.fetchone()[0]
	if int(tout)>0:
		delay=int(time.time())-int(tout)
		if int(delay)>MAX_DELAY:
			cu.execute("DELETE FROM cache WHERE link = '%s'" % req)
			c.commit()
			info=''
		else:
			cu.execute("SELECT data FROM cache WHERE link = '%s'" % req)
			c.commit()
			try:
				info = cu.fetchone()
				info = str(info).replace('%5C%22','')
				info = str(info).replace('%0A','')
				info = str(info).replace('%5Cn',' ')
				info = unquote(info)
				lastsym = info.rfind('}') + 1
				info = info[3:lastsym].decode()
			except:
				info = cu.fetchone()[0]
				info = unquote(str(info))
		return info
	else: return ''

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		infourl = urllib2.addinfourl(fp, headers, req.get_full_url())
		infourl.status = code
		infourl.code = code
		return infourl
	http_error_300 = http_error_302
	http_error_301 = http_error_302
	http_error_303 = http_error_302
	http_error_307 = http_error_302

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
urllib2.install_opener(opener)

def HTML(url, post = {}, decode = '', nocache = False, cookie = None):
	#if nocache == False:
	#	try:		html = get_inf_db(url+str(post))
	#	except:	html=''
	#else:
	html=''

	if len(html)<6:
		try:
			#'XBMC/' + xbmc_version + ' (' + xbmc_OS + ') ' + addon_name + '/' + addon_version
			headers = {'User-Agent':UserAgent[12:], 'Content-Type':'application/x-www-form-urlencoded'}

			if(url.find('www.blive.kg') > -1 or url.find('http://onlinetv.kg/XMLService') > -1):
				conn = urllib2.urlopen(urllib2.Request(url, urlencode(post), headers))
			elif(url.find('cinemaonline.kg') > -1):
				if(decode != ''):
					headers = {'User-Agent':UserAgent[12:]
					,'Host':'cinemaonline.kg'
					,'Origin':'http://cinemaonline.kg'
					,'Content-Type':'application/x-www-form-urlencoded'
					,'Accept':'*/*'
					,'Referer':'http://cinemaonline.kg/'
					,'Accept-Encoding':'gzip,deflate,sdch'
					,'Accept-Language':'ru,en-us;q=0.8,en;q=0.6'
					,'Cookie':decode}
				else:
					headers = {'User-Agent':UserAgent[12:]
					,'Host':'cinemaonline.kg'
					,'Origin':'http://cinemaonline.kg'
					,'Content-Type':'application/x-www-form-urlencoded'
					,'Accept':'*/*'
					,'Referer':'http://cinemaonline.kg/'
					,'Accept-Encoding':'gzip,deflate,sdch'
					,'Accept-Language':'ru,en-us;q=0.8,en;q=0.6'}
				opener = urllib2.build_opener(NoRedirectHandler())
				conn = opener.open(urllib2.Request(url, urlencode(post), headers))
			else:
				opener = urllib2.build_opener(NoRedirectHandler())
				conn = opener.open(urllib2.Request(url, urlencode(post), headers))
			conn.getcode()

			html = conn.read()
			#conn.close()

			if(url.find('cinemaonline.kg') == -1 and decode != ''):
				html = html.decode(decode)

			try:
				html = html.encode('utf-8')
				json.loads(html[24:-2])
				html = html[24:-2]
			except: pass

			#add_to_db(url+str(post),html)
		except: pass

	return html


def Colored(text = '', colorid = '', isBold = False):
	if colorid == 'nextpage':
		color = 'FF11b500'
	elif colorid == 'opendialog':
		color = 'FFe37101'
	elif colorid == 'light':
		color = 'FF42aae0'
	elif colorid == 'bright':
		color = 'F0FF00FF'
	elif colorid == 'bold':
		return '[B]' + text + '[/B]'
	else:
		color = colorid

	if isBold == True:
		text = '[B]' + text + '[/B]'
	if isBold == False:
		text = text.replace("[/B]","").replace("[B]","")

	return '[COLOR ' + color + ']' + text + '[/COLOR]'


def str2sec(time):
	try:
		times = map(int, re.split(r"[:]", time))
		if len(times) == 3:
			seconds = times[0]*3600+times[1]*60+times[2]
		elif len(times) == 2:
			seconds = times[0]*60+times[1]
		return seconds
	except:
		return 0


def ImagePath(name):
	return os.path.join(addon_imgpath, str(name))


def Noty(heading, message, icon = addon_icon, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))


def Message(title, text):
	dialog = xbmcgui.Dialog()
	dialog.ok(str(title), str(text))


hos = int(sys.argv[1])
def Request(params):
	return '%s?%s' % (sys.argv[0], urlencode(params))


def XBMCItem(i):
	try:    i['thumb']
	except: i['thumb'] = ''

	try:    i['plot']
	except: i['plot'] = ''

	try:    i['fanart']
	except: i['fanart'] = ''

	try:    i['size']
	except: i['size'] = ''

	try:    i['duration']
	except: i['duration'] = ''

	try:    i['year']
	except: i['year'] = ''

	try:    float(i['rating'])
	except: i['rating'] = float(0)

	try:    i['genre']
	except: i['genre'] = ''

	item = xbmcgui.ListItem(i['title'], iconImage='DefaultVideo.png', thumbnailImage=i['thumb'])

	if i['fanart']:
		item.setProperty('fanart_image', i['fanart'])

	item.setInfo('Video', {
		'title'      : i['title'],
		'plot'       : i['plot'],
		'plotoutline': i['plot'],
		'size'       : i['size'],
		'year'       : i['year'],
		'rating'     : i['rating'],
		'genre'      : i['genre']
		#'duration'   : int('30')#i['duration']
	})

	if i['duration']:
		item.addStreamInfo('video', {'duration':str2sec(i['duration'])})

	return item

def XBMCItemAdd(item = {}, request = {}, isFolder = True):
	try:
		func = request['func']
		return xbmcplugin.addDirectoryItem(handle=hos, url=Request(request), listitem=XBMCItem(item), isFolder=isFolder)
	except:
		return xbmcplugin.addDirectoryItem(handle=hos, url=request['url'], listitem=XBMCItem(item), isFolder=isFolder)


def XBMCEnd():
	return xbmcplugin.endOfDirectory(hos)

def XBMCPlay(params):
	xbmc.Player().play(params['url'])

def addLinkPlaylist(playlist, i):
	try:    i['thumb']
	except: i['thumb'] = ''

        try:    i['channelID']
        except: i['channelID'] = ''

	item = xbmcgui.ListItem(i['title'], iconImage="DefaultVideo.png", thumbnailImage=i['thumb'])
	item.setInfo( type="Video", infoLabels={'Title':i['title']} )
        item.setProperty('channelID',i['channelID'])
	#item.setLabel2('heelp')

	playlist.add(i['url'], item)

	return True

def run_settings(params):
	__addon__.openSettings()
	#xbmc.executebuiltin('Container.Update(%s?func=mainScreen)' % sys.argv[0])

def clear_cache(params):
	try:
		cu.execute("DELETE FROM cache")
		c.commit()
		Noty('KG OnTV', 'Кэш удалён')
	except:
		Noty('KG OnTV', 'Ошибка при удалении кэша :(')
