#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, json, urlparse, urllib
import xbmc, xbmcplugin, xbmcaddon
from BeautifulSoup import BeautifulSoup #4.3.1 not working
from Header import *


__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )

def NMCategories(params):
	try:
		namba_token = re.compile('<script>var CSRF_TOKEN=\'(.+?)\';</script>').findall(HTML('http://namba.kg/'))[0]
		
		html = BeautifulSoup(HTML(params['url']))

		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func' : 'NMSearch',
				'url'  : params['url'],
				'token': namba_token
			})
		XBMCItemAdd({'title':Colored('Поcледние поступления', 'FFCC4186')},
			{
				'func' : 'NMVideos',
				'mode' : 'last',
				'url'  : params['url'],
				'token': namba_token
			})
		XBMCItemAdd({'title':Colored('Популярные - ТОП 30', 'FFCC4186')},
			{
				'func' : 'NMVideos',
				'mode' : 'top30',
				'url'  : params['url'],
				'token': namba_token
			})

		for li in html.find('ul', {'class': 'categories-menu'}).findAll('li'):
			XBMCItemAdd({'title': li.a.string.encode('utf-8')},
				{
					'func' : 'NMVideos',
					'url'  : 'http://movie.namba.kg'+li.a['href'],
					'token': namba_token
				})
		XBMCEnd()
	except:
		Noty('Namba.Кинозал', 'Сервер недоступен', ImagePath('noty-namba-kg.png'))
	

def NMVideos(params):
	try:
		html = BeautifulSoup(HTML(params['url']))

		try   : mode = params['mode']
		except: mode = ''
		
		if mode != 'last' and mode != 'top30' and html.find('p', {'class':'pages'}):
			try   : page = '1' if int(params['page']) < 1 else params['page']
			except: page = '1'

			maxpage = re.compile(', ([0-9]+?),').findall(re.sub('\s+', ' ', html.find('p', {'class':'pages'}).parent.script.string))[0].encode('utf-8')
			XBMCItemAdd({'title':Colored('[ Перейти на страницу ]', 'opendialog')+' '+page+' из '+maxpage+' страниц', 'thumb':ImagePath('findpage.png')},
				{
					'func': 'NMPages',
					'page': int(page),
					'token':params['token'],
					'url' : params['url']
				})

			if int(page) < int(maxpage):
				parsed = urlparse.urlparse(params['url'])
				try:    catID = 'http://movie.namba.kg/category.php?id='+urlparse.parse_qs(parsed.query)['id'][0]
				except: catID = 'http://movie.namba.kg/search.php?q='+urlparse.parse_qs(parsed.query)['q'][0]
				XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
					{
						'func': 'NMVideos',
						'page': int(page) + 1,
						'token':params['token'],
						'url' : catID+'&p='+str(int(page) + 1)
					})

			
				
		resultBlockID = 1 if mode == 'last' else 0

		videolist = html.findAll('ul', {'class': 'result-block'})[resultBlockID].findAll('div', {'class': ['thumb-small', 'thumb']})
		if len(videolist) == 0:
			Noty('Namba.Кинозал','Фильмы не найдены', ImagePath('noty-namba-kg.png'))
			NMCategories(params)
		else:
			for div in videolist:
				try:
					html = HTML('http://movie.namba.kg'+div.a['href'])
					video_id = re.compile('<param value="config=.+?__(.+?)" name="flashvars">').findall(html)[0]

					parsed = urlparse.urlparse(div.a['href'])
					watch_id = urlparse.parse_qs(parsed.query)['id'][0]
					#watch_id = re.compile('id=([0-9]+)').findall(div.a['href'])[0]

					json_namba = json.loads(HTML('http://namba.kg/api/?service=video&action=video&token='+params['token']+'&id='+video_id))
				
					title = json_namba['video']['title']
					video_url = json_namba['video']['download']['flv']
					XBMCItemAdd({'title':title.encode('utf-8'), 'thumb':div.a.img['src']},
						{
							'url' : video_url
						}, False)
				except:
					Noty('Namba.Кинозал', 'Файл с ошибкой пропущен', ImagePath('noty-namba-kg.png'))
		XBMCEnd()
	except:
		Noty('Namba.Кинозал', 'Сервер недоступен', ImagePath('noty-namba-kg.png'))
	

def NMSearch(params):
	keyboard = xbmc.Keyboard('','Namba.Кинозал: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		NMVideos({'url':'http://movie.namba.kg/search.php?q='+urllib.quote(keyboard.getText()), 'token':params['token']})

def NMPages(params):
	keyboard = xbmc.Keyboard('','Namba.Кинозал: Перейти на страницу', False)
	keyboard.doModal()   
	parsed = urlparse.urlparse(params['url'])
	try:    catID = 'http://movie.namba.kg/category.php?id='+urlparse.parse_qs(parsed.query)['id'][0]
	except: catID = 'http://movie.namba.kg/search.php?q='+urlparse.parse_qs(parsed.query)['q'][0]
	if keyboard.isConfirmed():
		try:    page = int(keyboard.getText())
		except: page = 0

		NMVideos({'url':catID+'&p='+str(page), 'token':params['token'], 'page':str(page)})