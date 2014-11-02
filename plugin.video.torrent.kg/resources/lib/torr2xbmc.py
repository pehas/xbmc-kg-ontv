#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib, urllib, urllib2, re, sys, os, socket, base64, urlparse
import xbmcplugin, xbmcgui, xbmcaddon, xbmc, xbmcaddon
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from TSCore import TSengine as tsengine

hos                = int(sys.argv[1])
sock               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

xbmc_version       = xbmc.getInfoLabel('System.BuildVersion')
xbmc_platform      = os.environ.get( 'OS', '' ).lower().replace( 'xbox', "XBox" ).replace( 'win32', 'Windows' ).replace( 'linux', 'GNU/Linux' ).replace( 'osx', 'Mac OS X' )
if not xbmc_platform: xbmc_platform = 'Unknown OS'

__addon__          = xbmcaddon.Addon( id = 'plugin.video.torrent.kg' )
__language__       = __addon__.getLocalizedString

addon_icon         = __addon__.getAddonInfo('icon')
addon_fanart       = __addon__.getAddonInfo('fanart')
addon_path         = __addon__.getAddonInfo('path')
addon_type         = __addon__.getAddonInfo('type')
addon_id           = __addon__.getAddonInfo('id')
addon_author       = __addon__.getAddonInfo('author')
addon_name         = __addon__.getAddonInfo('name')
addon_version      = __addon__.getAddonInfo('version')
img_path           = os.path.join(addon_path, 'resources', 'media')

torrentkg_login    = __addon__.getSetting('torrentkg_login')
torrentkg_password = __addon__.getSetting('torrentkg_password')
prt_file           = __addon__.getSetting('port_path')
aceport            = 62062
try:
	if prt_file: 
		gf = open(prt_file, 'r')
		aceport=int(gf.read())
		gf.close()
except: prt_file=None

if not prt_file:
	try:
		fpath= os.path.expanduser("~")
		pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
		gf = open(pfile, 'r')
		aceport=int(gf.read())
		gf.close()
		__addon__.setSetting('port_path',pfile)
		print aceport
	except: aceport=62062
	
# JSON понадобится, когда будет несколько файлов в торренте
try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def AllowForumID(forumID):
	blacklist = [574, 255, 726, 379, 663, 790, 779, 919, 970, 920, 971, 303, 205, 565, 776, 750, 740, 307, 111, 577, 366, 130]
	if int(forumID) in blacklist:
		return False
	else:
		return True

def GET_HTML(request):
	class NoRedirectHandler(urllib2.HTTPRedirectHandler):
		def http_error_302(self, req, fp, code, msg, headers):
			infourl = urllib.addinfourl(fp, headers, req.get_full_url())
			infourl.status = code
			infourl.code = code
			return infourl
		http_error_300 = http_error_302
		http_error_301 = http_error_302
		http_error_303 = http_error_302
		http_error_307 = http_error_302

	opener = urllib2.build_opener(NoRedirectHandler())
	urllib2.install_opener(opener)
	try:    request['url']
	except: return ''

	try:    request['post']
	except: request['post'] = {}
	
	try:    request['cookie']
	except: request['cookie'] = ''
	
	try:    request['decode']
	except: request['decode'] = ''
	
	try:    request['get-cookie']
	except: request['get-cookie'] = False
	
	try:
		headers = {'User-Agent':'XBMC/' + xbmc_version + ' (' + xbmc_platform + ') ' + addon_name + '/' + addon_version, 'Cookie':request['cookie'], 'Content-Type':'application/x-www-form-urlencoded'}
		conn = urllib2.urlopen(urllib2.Request(request['url'], urllib.urlencode(request['post']), headers))
		
		if request['get-cookie']:
			try :   return conn.headers['Set-Cookie']
			except: return 'false'
		
		html = conn.read()
		conn.close()
		
		if request['decode']: html = html.decode(request['decode'])
		
		return html
	except: return ''

def showMessage(heading, message, times = 3000, pics = os.path.join(img_path, 'icon_torrentkg.png')):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def message(title, text):
    dialog = xbmcgui.Dialog()
    dialog.ok(str(title), str(text))

def _auth():
	try:
		url              = 'http://www.torrent.kg/forum/login.php'
		test_cookie      = GET_HTML({'url':url, 'get-cookie':True})
		temp_cookie      = GET_HTML({'url':url, 'post':{'login_username':torrentkg_login,'login_password':torrentkg_password,'login':'Вход'}, 'cookie':test_cookie, 'get-cookie':True})
		temp             = temp_cookie.split(',')
		torrentkg_cookie = (temp[2] + temp[3]).strip()
		return torrentkg_cookie
	except:
		showMessage('torrent.kg', 'Ошибка авторизации', 4000, os.path.join(img_path, 'icon_torrentkg.png'))
		return False

baseurl = 'http://www.torrent.kg/forum/'

def torrentkg_SearchResults(params):
	html = BeautifulSoup(GET_HTML({'url':params['url'], 'post':params['post'], 'cookie':params['cookie']}))
	for tr in html.find('table', attrs={'class':'forumline'}).findAll('tr', attrs={'class':'tCenter'}):
		link  = baseurl+tr.find('a', attrs={'class':'med dLink'})['href']
		size  = tr.find('td', attrs={'class':'row4 small nowrap'}).string.replace('&nbsp;', ' ')
		SL    = '[ [COLOR F000EE00]' + tr.find('td', attrs={'class':'row4 seedmed'}).b.string + '[/COLOR] | [COLOR F0FF0000]' + tr.find('td', attrs={'class':'row4 leechmed'}).b.string + '[/COLOR] | [COLOR E0FFFFFF]' + size + '[/COLOR] ] '
		title = SL.encode('utf-8') + tr.findAll('a', attrs={'class':['genmed', 'seedmed']}, text=True)[7].strip().encode('utf-8')
		li    = xbmcgui.ListItem(title)
		uri   = construct_request({
				'func'   : 'torrentkg_play',
				'url'    : link,
				'cookie' : params['cookie']
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def torrentkg_Page01(params):
	torrentkg_cookie = _auth()

	if torrentkg_cookie:
		try:
			li = xbmcgui.ListItem('[COLOR FFF5DEB3][B][ Поиск ][/B][/COLOR]')
			uri = construct_request({
				'func'   : 'torrentkg_SearchDialog',
				'url'    : 'http://www.torrent.kg/forum/tracker.php',
				'cookie' : torrentkg_cookie
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)

			url = baseurl
			html = BeautifulSoup(GET_HTML({'url':url, 'cookie':torrentkg_cookie}))
			for category in html.findAll('div', attrs={'class':'category'})[2].findAll('h4', attrs={'class':'forumlink'}):
				link  = baseurl+category.a['href']
				title = category.a.string.encode('utf-8')
				li    = xbmcgui.ListItem(title)
				parsed = urlparse.urlparse(link)
				if urlparse.parse_qs(parsed.query)['f'][0] == '299':
					uri   = construct_request({
						'func':'torrentkg_Page03',
						'url':link,
						'cookie':torrentkg_cookie
					})
				else:
					uri   = construct_request({
						'func':'torrentkg_Page02',
						'url':link,
						'cookie':torrentkg_cookie
					})
				xbmcplugin.addDirectoryItem(hos, uri, li, True)
			xbmcplugin.endOfDirectory(hos)
		except:
			pass
	else:
		message('torrent.kg', 'Сервер недоступен или некорректные логин/пароль.')

def torrentkg_Page02(params):
	html = BeautifulSoup(GET_HTML({'url':params['url'], 'cookie':params['cookie']}))
	for category in html.findAll('h4', attrs={'class':'forumlink'}):
		parsed = urlparse.urlparse(category.a['href'])
		if AllowForumID(urlparse.parse_qs(parsed.query)['f'][0]):
			link  = baseurl+category.a['href']
			title = category.a.string.encode('utf-8')
			li    = xbmcgui.ListItem(title)
			uri   = construct_request({
					'func':'torrentkg_Page03',
					'url':link,
					'cookie':params['cookie']
				})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def torrentkg_Page03(params):
	html = BeautifulSoup(GET_HTML({'url':params['url'], 'cookie':params['cookie']}))
	for tr in html.findAll('tr', attrs={'class':'forum_topic'}):
		if tr.find('span', attrs={'class':'leechmed'}) != None:
			link_topic = baseurl+tr.find('a', attrs={'class':'torTopic'})['href']
			link_temp  = tr.find('td', attrs={'class':'tCenter nowrap'}).findAll('div')[2].a
			link  = baseurl+link_temp['href']
			size  = link_temp.string.replace('&nbsp;', ' ')
			SL    = '[ [COLOR F000EE00]' + tr.find('span', attrs={'class':'seedmed'}).b.string + '[/COLOR] | [COLOR F0FF0000]' + tr.find('span', attrs={'class':'leechmed'}).b.string + '[/COLOR] | [COLOR E0FFFFFF]' + size + '[/COLOR] ] '
			title = SL.encode('utf-8') + (str(tr.find('a', attrs={'class':'torTopic'}).b.string).decode('utf-8').encode('utf-8')).strip()
			li    = xbmcgui.ListItem(title)
			uri   = construct_request({
					'func'   : 'torrentkg_play',
					'url'    : link,
					'cookie' : params['cookie']
				})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

	
def torrentkg_play(params):
	torr_link = base64.b64encode(GET_HTML({'url':params['url'], 'cookie':params['cookie']}))
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
	TSplayer = tsengine()
	out      = TSplayer.load_torrent(torr_link, 'RAW', port=aceport)
	if out == 'Ok':
		for k,v in TSplayer.files.iteritems():
			li  = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url' : torr_link,
				'title'    : k,
				'ind'      : v,
				'img'      : None,
				'func'     : 'play_it'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
	xbmcplugin.endOfDirectory(hos)
	TSplayer.end()

"""-----------------------------------------------------
	 [ torrent.kg ] Поиск по сайту
-----------------------------------------------------"""
def torrentkg_SearchDialog(params):
	keyboard = xbmc.Keyboard('','torrent.kg: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		torrentkg_SearchResults({'url':params['url'], 'post':[('f[]', '4'), ('f[]', '773'), ('f[]', '485'), ('f[]', '310'), ('f[]', '309'), ('f[]', '775'), ('f[]', '144'), ('f[]', '924'), ('f[]', '278'), ('f[]', '133'), ('f[]', '66'), ('f[]', '86'), ('f[]', '121'), ('f[]', '630'), ('f[]', '238'), ('f[]', '5'), ('f[]', '928'), ('f[]', '701'), ('f[]', '490'), ('f[]', '728'), ('f[]', '258'), ('f[]', '145'), ('f[]', '823'), ('f[]', '6'), ('f[]', '154'), ('f[]', '156'), ('f[]', '155'), ('f[]', '254'), ('f[]', '604'), ('f[]', '742'), ('f[]', '741'), ('f[]', '912'), ('f[]', '283'), ('f[]', '1013'), ('f[]', '217'), ('f[]', '445'), ('f[]', '216'), ('f[]', '178'), ('f[]', '816'), ('f[]', '573'), ('f[]', '778'), ('f[]', '785'), ('f[]', '780'), ('f[]', '786'), ('f[]', '783'), ('f[]', '787'), ('f[]', '784'), ('f[]', '782'), ('f[]', '788'), ('f[]', '1046'), ('f[]', '755'), ('f[]', '542'), ('f[]', '789'), ('f[]', '779'), ('f[]', '7'), ('f[]', '491'), ('f[]', '918'), ('f[]', '193'), ('f[]', '192'), ('f[]', '190'), ('f[]', '189'), ('f[]', '188'), ('f[]', '187'), ('f[]', '821'), ('f[]', '168'), ('f[]', '517'), ('f[]', '516'), ('f[]', '515'), ('f[]', '548'), ('f[]', '557'), ('f[]', '518'), ('f[]', '519'), ('f[]', '520'), ('f[]', '521'), ('f[]', '522'), ('f[]', '920'), ('f[]', '83'), ('f[]', '464'), ('f[]', '563'), ('f[]', '457'), ('f[]', '204'), ('f[]', '203'), ('f[]', '207'), ('f[]', '564'), ('f[]', '202'), ('f[]', '567'), ('f[]', '76'), ('f[]', '1044'), ('f[]', '652'), ('f[]', '358'), ('f[]', '356'), ('f[]', '225'), ('f[]', '917'), ('f[]', '614'), ('f[]', '613'), ('f[]', '735'), ('f[]', '734'), ('f[]', '733'), ('f[]', '357'), ('f[]', '826'), ('f[]', '632'), ('f[]', '359'), ('f[]', '336'), ('f[]', '983'), ('f[]', '939'), ('f[]', '746'), ('f[]', '745'), ('f[]', '747'), ('f[]', '769'), ('f[]', '824'), ('f[]', '825'), ('f[]', '812'), ('f[]', '752'), ('f[]', '749'), ('f[]', '748'), ('f[]', '286'), ('f[]', '908'), ('f[]', '740'), ('f[]', '307'), ('f[]', '634'), ('f[]', '645'), ('f[]', '65'), ('f[]', '119'), ('f[]', '633'), ('f[]', '182'), ('f[]', '489'), ('f[]', '650'), ('f[]', '731'), ('f[]', '646'), ('f[]', '599'), ('f[]', '593'), ('f[]', '820'), ('f[]', '288'), ('f[]', '299'), ('f[]', '13'), ('f[]', '561'), ('f[]', '441'), ('f[]', '285'), ('f[]', '284'), ('f[]', '727'), ('f[]', '231'), ('f[]', '224'), ('f[]', '223'), ('f[]', '222'), ('f[]', '221'), ('f[]', '220'), ('f[]', '219'), ('f[]', '985'), ('f[]', '988'), ('f[]', '638'), ('f[]', '766'), ('f[]', '545'), ('f[]', '323'), ('f[]', '966'), ('f[]', '472'), ('f[]', '601'), ('f[]', '268'), ('f[]', '941'), ('f[]', '1010'), ('f[]', '471'), ('f[]', '277'), ('f[]', '964'), ('f[]', '579'), ('f[]', '965'), ('f[]', '659'), ('f[]', '279'), ('f[]', '677'), ('f[]', '444'), ('f[]', '629'), ('f[]', '339'), ('f[]', '611'), ('f[]', '592'), ('f[]', '1047'), ('f[]', '756'), ('f[]', '986'), ('f[]', '990'), ('f[]', '989'), ('f[]', '44'), ('f[]', '544'), ('f[]', '96'), ('f[]', '703'), ('f[]', '276'), ('f[]', '969'), ('f[]', '947'), ('f[]', '301'), ('f[]', '364'), ('f[]', '291'), ('f[]', '232'), ('f[]', '702'), ('f[]', '169'), ('f[]', '87'), ('f[]', '237'), ('f[]', '942'), ('f[]', '293'), ('f[]', '180'), ('f[]', '292'), ('f[]', '547'), ('f[]', '581'), ('f[]', '580'), ('f[]', '371'), ('f[]', '354'), ('f[]', '658'), ('f[]', '380'), ('f[]', '594'), ('f[]', '57'), ('f[]', '793'), ('f[]', '363'), ('f[]', '79'), ('f[]', '84'), ('f[]', '161'), ('f[]', '583'), ('f[]', '244'), ('f[]', '569'), ('f[]', '234'), ('f[]', '172'), ('f[]', '470'), ('f[]', '751'), ('f[]', '316'), ('f[]', '417'), ('f[]', '681'), ('f[]', '423'), ('f[]', '546'), ('f[]', '730'), ('f[]', '302'), ('f[]', '271'), ('f[]', '596'), ('f[]', '257'), ('f[]', '1036'), ('f[]', '1037'), ('f[]', '603'), ('f[]', '514'), ('f[]', '582'), ('f[]', '1038'), ('f[]', '560'), ('f[]', '978'), ('f[]', '218'), ('f[]', '631'), ('f[]', '1043'), ('f[]', '177'), ('f[]', '1042'), ('f[]', '1041'), ('f[]', '1040'), ('f[]', '1039'), ('f[]', '952'), ('f[]', '758'), ('f[]', '654'), ('f[]', '951'), ('f[]', '102'), ('f[]', '267'), ('f[]', '487'), ('f[]', '984'), ('f[]', '1007'), ('f[]', '1008'), ('f[]', '1009'), ('f[]', '122'), ('f[]', '249'), ('f[]', '618'), ('f[]', '246'), ('f[]', '617'), ('f[]', '247'), ('f[]', '245'), ('f[]', '598'), ('f[]', '616'), ('f[]', '250'), ('submit', '  Поиск  '), ('sd','1'), ('nm',str(keyboard.getText()).decode('utf-8').encode('windows-1251'))], 'cookie':params['cookie']})
	else:
		torrentkg_Page01({})
	
def ttv (params):
	beautifulSoup = BeautifulSoup(GET_HTML({'url':'http://torrent-tv.ru/channels.php'}))
	channels = beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
	for ch in channels: 
		link  = ch.find('a')['href']
		title = ch.find('strong').string.encode('utf-8')
		img   = 'http://torrent-tv.ru/'+ch.find('img')['src']
		li    = xbmcgui.ListItem(title,img,img)
		uri   = construct_request({
				'func': 'play_ch',
				'img':img,
				'title':title,
				'file':link
			})
		xbmcplugin.addDirectoryItem(hos, uri, li)
	xbmcplugin.endOfDirectory(hos)
	
def play_ch(params):
	http = GET_HTML({'url':'http://torrent-tv.ru/'+params['file']})
	beautifulSoup = BeautifulSoup(http)
	tget= beautifulSoup.find('div', attrs={'class':'tv-player-wrapper'})
	#print tget
	#this.loadTorrent("http://94.242.221.195:7773/file?name=%D0%A2%D0%9D%D0%A2"
	#print http
	#print 'http://torrent-tv.ru/'+params['file']
	m=re.search('http:(.+)"', str(tget))
	torr_link= m.group(0).split('"')[0]
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
	TSplayer.end()
	showMessage('Торрент', 'Стоп', 2000, os.path.join(img_path, 'icon_torrenttvru.png'))

def mainScreen(params):
	li = xbmcgui.ListItem('torrent.kg', os.path.join(img_path, 'torrentkg.png'), os.path.join(img_path, 'torrentkg.png'))
	uri = construct_request({
		'func': 'torrentkg_Page01'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('ТОРРЕНТ-ТВ: [COLOR FFD2FFCF]Эксперементально. Возможна "внешка"[/COLOR]', os.path.join(img_path, 'torrenttvru.png'), os.path.join(img_path, 'torrenttvru.png'))
	uri = construct_request({
		'func': 'ttv'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def play_it(params):
	torr_link=params['torr_url']	
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'RAW',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(int(params['ind']),params['title'],addon_icon,params['img'])
	TSplayer.end()
	showMessage('Торрент', 'Стоп', 2000, os.path.join(img_path, 'icon_torrentkg.png'))    
		
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param

def addon_main():
	#xbmc.log( '[s]: play' , 2 )
	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		mainScreen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)

