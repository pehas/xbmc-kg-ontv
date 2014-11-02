#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__ = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )

def TSCategories(params):
	try:
		siteurl = 'anime.ts.kg' if params['url'].find('anime.ts.kg') > -1 else 'www.ts.kg'
		html = BeautifulSoup(HTML(params['url']))

		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'TSSearch',
				'url' : params['url']
			})
		XBMCItemAdd({'title':Colored('Последние поступления', 'light', True)},
			{
				'func': 'TSNew',
				'url' : 'http://' + siteurl + '/'
			})

		for li in html.find('ul', attrs={'class':'nav nav-tabs'}).findAll('li', recursive=False):
			try:    subcategory = li['class']
			except: subcategory = None

			if subcategory:
				li.a.b.extract()
				subcategoryTitle = li.a.string
				for li in li.ul.findAll('li'):
					XBMCItemAdd({'title': (subcategoryTitle + ' - ' + li.a.string).encode('utf-8'), 'thumb':ImagePath('tv-shows.png')},
						{
							'func': 'TSTVShows',
							'url' : li.a['href']
						})
			else:
				if li.a['href'].find(params['url']) > -1:
					XBMCItemAdd({'title': li.a.string.encode('utf-8'), 'thumb':ImagePath('tv-shows.png')},
						{
							'func': 'TSTVShows',
							'url' : li.a['href']
						})
		XBMCEnd()
	except:
		Noty('TS.KG', 'Сервер недоступен', ImagePath('noty-tskg.png'))
	

def TSTVShows(params):
	try:
		html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url'])))
		try:
			mode = params['search']
			tvshows = html.findAll('li')
			if len(tvshows) > 0:
				for tvshow in tvshows:
					XBMCItemAdd({'title':tvshow.a.string.encode('utf-8')},
						{
							'func' : 'TSSeasons',
							'title': tvshow.a.string.encode('utf-8'),
							'url'  : tvshow.a['href']
						})
				XBMCEnd()
			else:
				Noty('TS.KG', 'Видео не найдено', ImagePath('noty-tskg.png'))
		except:
			tvshows = html.findAll('div', attrs={'class':'categoryblocks'})
			if len(tvshows) > 0:
				for tvshow in tvshows:
					XBMCItemAdd({'title':tvshow.a.img['title'].encode('utf-8'), 'thumb':tvshow.a.img['src']},
						{
							'func' : 'TSSeasons',
							'title': tvshow.a.img['title'].encode('utf-8'),
							'url'  : tvshow.a['href'],
							'thumb': tvshow.a.img['src']
						})
				XBMCEnd()
			else:
				Noty('TS.KG', 'Видео не найдено', ImagePath('noty-tskg.png'))
	except:
		Noty('TS.KG', 'Сервер недоступен', ImagePath('noty-tskg.png'))

def TSSeasons(params):
	try:
		siteurl = 'anime.ts.kg' if params['url'].find('anime.ts.kg') > -1 else 'www.ts.kg'

		if(siteurl == 'anime.ts.kg'):
			html = re.compile('="http://'+siteurl+'/pls/(.+?)/(.+?)"><').findall(re.sub('\s+', ' ', HTML(params['url'])))
			for tv_show, season in html:
				XBMCItemAdd({'title':params['title']+': Сезон '+season}, {'url' : 'http://'+siteurl+'/pls/'+tv_show+'/'+season+'/all.pls'}, False)
			XBMCEnd()
		else:
			seasons_numbers = re.compile('<ul class="breadcrumb" id="season-(.+?)">').findall(re.sub('\s+', ' ', HTML(params['url'])))
			for season in seasons_numbers:
				XBMCItemAdd({'title':params['title']+': Сезон '+season},
					{
						'func'  : 'TSEpisodes',
						'url'   : params['url'] + '/' + season + '/1',
						'title' : params['title'],
						'season': season
					}, False)
			XBMCEnd()
	except:
		Noty('TS.KG', 'Сервер недоступен', ImagePath('noty-tskg.png'))

def TSEpisodes(params):
	try:
		tskgplaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		tskgplaylist.clear()
		series = HTML(params['url'])
		series_urls = re.compile('url:\'(.+?)\',eventCategory').findall(series)
		for series_url in series_urls:
			title = params['title'] + ': s' + params['season'] + 'e' + os.path.basename(series_url)[:-4]
			addLinkPlaylist(tskgplaylist, {'title':title, 'url':series_url+UserAgent})
		xbmc.executebuiltin("ActivateWindow(VideoPlaylist)")
	except:
		Noty('TS.KG', 'Сервер недоступен', ImagePath('noty-tskg.png'))

def TSNew(params):
	try: 
		try:
			tskg_news_count = int(__addon__.getSetting('tskg_news_count'))
		except:
			tskg_news_count = 1
		tskg_news_count += 2

		siteurl = 'http://anime.ts.kg/' if params['url'].find('anime.ts.kg') > -1 else 'http://www.ts.kg/'
		replaceurl = 'http://anime.ts.kg/video/' if params['url'].find('anime.ts.kg') > -1 else 'http://node1.ts.kg/video/'

		html = BeautifulSoup(HTML(url=params['url'], nocache=True))
		news = html.find('table', {'class':'news-table'})
		today = 0
		for tr in news.findAll('tr'):
			if tr.td.h3 != None:
				news_date = ('[' + tr.td.h3.string + '] ').encode('utf-8')
				today+=1

			if today < tskg_news_count:
				try:
					td = tr.findAll('td')[1]
					if td.span == None:
						if(siteurl == 'http://anime.ts.kg/'):
							url = td.a['href'].replace(siteurl, replaceurl) + '.mp4'
						else:
							html = HTML(td.a['href'])
							url = re.compile('url:\'(.+?)\',eventCategory').findall(html)[0]
						
						XBMCItemAdd({'title':news_date + '[B]' + td.a.string.encode('utf-8') + '[/B]'}, {'url':url+UserAgent}, False)
					else:
						if td.a.string.encode('utf-8').find('Эпизод') > -1:
							if(siteurl == 'http://anime.ts.kg/'):
								url = td.a['href'].replace(siteurl, replaceurl) + '.mp4'
							else:
								html = HTML(td.a['href'])
								url = re.compile('url:\'(.+?)\',eventCategory').findall(html)[0]
							
							XBMCItemAdd({'title':news_date + (' [COLOR FF11b500]' + td.span.string + '[/COLOR]  [B]' + td.a.string + '[/B]  [' + td.a['data-original-title'] + ']').encode('utf-8')}, {'url':url+UserAgent}, False)
						else:
							XBMCItemAdd({'title':news_date + (' [COLOR FF11b500]' + td.span.string + '[/COLOR]  [B]' + td.a.string + '[/B]  [' + td.a['data-original-title'] + ']').encode('utf-8')},
							{
								'func' : 'TSSeasons',
								'title': td.a.string.encode('utf-8'),
								'url'  : td.a['href']
							})
				except: pass
		XBMCEnd()
	except:
		Noty('TS.KG', 'Сервер недоступен', ImagePath('noty-tskg.png'))

def TSSearch(params):
	keyboard = xbmc.Keyboard('','TS.KG: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		TSTVShows({'url':params['url']+'search/'+keyboard.getText(), 'search':True})