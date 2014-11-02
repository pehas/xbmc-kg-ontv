#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, json, urlparse
import xbmc, xbmcplugin, xbmcaddon
from BeautifulSoup import BeautifulSoup #4.3.1 not working
from Header import *

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
nambakg_login    = __addon__.getSetting('nambakg_login')
nambakg_password = __addon__.getSetting('nambakg_password')

def NSCategories(params):
	try:
		namba_token = re.compile('<script>var CSRF_TOKEN=\'(.+?)\';</script>').findall(HTML('http://namba.kg/'))[0]
		
		html = BeautifulSoup(HTML(params['url']))

		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func' : 'NSSearch',
				'url'  : params['url'],
				'token': namba_token
			})
	
		XBMCItemAdd({'title':Colored('Избранное', 'FFCC4186')},
			{
				'func' : 'NSTVShows',
				'mode' : 'favorite',
				'url'  : params['url'],
				'token': namba_token
			})
		
		XBMCItemAdd({'title':Colored('Новые сериалы', 'FFCC4186')},
			{
				'func' : 'NSTVShows',
				'mode' : 'newserials',
				'url'  : params['url'],
				'token': namba_token
			})
		XBMCItemAdd({'title':Colored('Новые серии', 'FFCC4186')},
			{
				'func' : 'NSTVShows',
				'mode' : 'newepisodes',
				'url'  : params['url'],
				'token': namba_token
			})
		XBMCItemAdd({'title':Colored('Популярные - ТОП 30', 'FFCC4186')},
			{
				'func' : 'NSTVShows',
				'mode' : 'top30',
				'url'  : params['url'],
				'token': namba_token
			})

		for li in html.find('ul', {'class':'categories-menu'}).findAll('li'):
			#if a.parent.name == 'li':
			#	try:    li_class = a.parent['class']
			#	except: li_class = ''
			#	if (a.parent.parent.name == 'div') and li_class != 'single-cate':
			#		title = (a.parent.parent.div.string + ' - ' + a.string).encode('utf-8')
			#	elif a.parent.parent.name == 'ul':
			#		title = (a.parent.parent.find('div', attrs={'class':'serials-subcategory-title grey'}).string + ' - ' + a.string).encode('utf-8')
			#	else:
			#		title = a.string.encode('utf-8')

				XBMCItemAdd({'title': li.a.string.encode('utf-8')},
					{
						'func' : 'NSTVShows',
						'url'  : 'http://serials.namba.kg'+li.a['href'],
						'token': namba_token
					})
		XBMCEnd()
	except:
		Noty('Namba.Сериалы', 'Сервер недоступен', ImagePath('noty-namba-kg.png'))

def NSTVShows(params):
	try:
		try   : mode = params['mode']
		except: mode = ''

		try   : search = params['search']
		except: search = None

		if mode == 'favorite':
			HTML('http://namba.kg/api/', {'token':params['token'], 'remember':'on', 'service':'user', 'action':'login', 'password':nambakg_password, 'login':nambakg_login})
			
			try:
				favor = BeautifulSoup(HTML(params['url'])).find('a', attrs={'href':re.compile('/favorite.php\?user=.+')})
				html = BeautifulSoup(HTML('http://serials.namba.kg'+favor['href']))
				tvshowslist = html.find('ul', {'class':'serials-list'}).findAll('li')
			except:
				Noty('Namba.Сериалы', 'Ошибка авторизации', ImagePath('noty-namba-kg.png'))
				
		elif mode == 'newserials' or search != None:
			html = BeautifulSoup(HTML(params['url']))
			tvshowslist = html.find('ul', {'class':'last-serials serials-list'}).findAll('li')
		elif mode == 'newepisodes':
			html = BeautifulSoup(HTML(params['url']))
			tvshowslist = html.find('ul', {'class':'new-episode-serials serials-list'}).findAll('li')
		elif mode == 'top30':
			html = BeautifulSoup(HTML(params['url']))
			tvshowslist = html.find('ul', {'class':'charts-result-block'}).findAll('li')
		else:
			html = BeautifulSoup(HTML(params['url']))
			tvshowslist = html.find('ul', {'class':'serials-list'}).findAll('li')

		if len(tvshowslist) > 0:
			for li in tvshowslist:
				lowertitle = li.a.img['title'].lower().encode('utf-8')
				title = li.a.img['title'].encode('utf-8')
				if (search != None and lowertitle.find(search.lower()) > -1) or search == None:
					XBMCItemAdd({'title':title, 'thumb':li.a.img['src']},
						{
							'func': 'NSSeasons',
							'url' : 'http://serials.namba.kg'+li.a['href'],
							'token': params['token'],
							'title': title + '  |  '
						})
			XBMCEnd()
		else:
			Noty('Namba.Сериалы', 'Фильмы не найдены', ImagePath('noty-namba-kg.png'))
	except:
		Noty('Namba.Сериалы', 'Сервер недоступен', ImagePath('noty-namba-kg.png'))

def NSSeasons(params):
	try:
		html = re.compile('<div class="panel-title">Сезон (.+?)</div>').findall(HTML(params['url']))
		parsed = urlparse.urlparse(params['url'])
		serial_id = urlparse.parse_qs(parsed.query)['id'][0]
		for season in html:
			XBMCItemAdd({'title':params['title'] + 'Сезон ' + season},
				{
					'func' : 'NSEpisodes',
					'url'  : 'http://serials.namba.kg/season.php?serial_id='+serial_id+'&season_id='+season,
					'token': params['token'],
					'title': 'Сезон ' + season + '  |  '
				}, False)
		XBMCEnd()
	except:
		Noty('Namba.Сериалы', 'Сервер недоступен', ImagePath('noty-namba-kg.png'))

def NSEpisodes(params):
	try:
		html = BeautifulSoup(HTML(params['url']))
		xbmc.executebuiltin("Action(Stop)")
		nambaplaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		nambaplaylist.clear()
		for li in html.find('ul', attrs={'class':'videos-pane'}).findAll('li'):
			try:
				html = HTML('http://serials.namba.kg'+li.a['href'])
				video_id = re.compile('<param value="config=.+?__(.+?)" name="flashvars">').findall(html)[0]
				json_namba = json.loads(HTML('http://namba.kg/api/?service=video&action=video&token='+params['token']+'&id='+video_id))
				video_url = json_namba['video']['download']['flv']
				title = params['title'] + li.find('div', attrs={'class':'grey'}).string.encode('utf-8')
				#XBMCItemAdd({'title': params['title'] + li.find('div', attrs={'class':'grey'}).string.encode('utf-8'), 'thumb':li.a.img['src']}, {'url' : video_url}, False)
				addLinkPlaylist(nambaplaylist, {'title':title, 'url':video_url, 'thumb':li.a.img['src']})
			except:
				Noty('Namba.Сериалы', 'Файл с ошибкой пропущен', ImagePath('noty-namba-kg.png'))
		xbmc.executebuiltin("ActivateWindow(VideoPlaylist)")
	except:
		Noty('Namba.Сериалы', 'Сервер недоступен', ImagePath('noty-namba-kg.png'))

def NSSearch(params):
	keyboard = xbmc.Keyboard('','Namba.Сериалы: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		NSTVShows({'url':'http://serials.namba.kg/all_serials.php', 'search':str(keyboard.getText()), 'token':params['token']})