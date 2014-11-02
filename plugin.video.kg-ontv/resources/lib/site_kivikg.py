#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, math
import xbmc, xbmcplugin, xbmcaddon

from BeautifulSoup import BeautifulSoup #4.3.1 not working
from Header import *
base_url = 'http://kivi.kg'
__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
def KVCategories(params):
	try:
		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'KVSearch',
				'status_line':'Поиск',
				'url' : params['url']
			})
		XBMCItemAdd({'title':Colored('Поступления на сайт', 'light')},
			{
				'func': 'KVMovies',
				'status_line':'Категория: Поступления на сайт',
				'url' : 'http://kivi.kg/index.php?option=com_virtuemart&page=shop.browse&category_id=27&Itemid=1'
			})
		
		html = BeautifulSoup(HTML(params['url']))
		for link in html.find('table').findAll('a', {'class':'mainlevel'}):
			url = link['href']
			title = link.string.encode('utf-8')
			if(url == '/index.php?option=com_virtuemart&Itemid=1'):
				url = 'http://kivi.kg/index.php?option=com_virtuemart&category_id=26&page=shop.browse&Itemid=1'
			if(url != '/index.php?option=com_virtuemart&Itemid=31'):
				XBMCItemAdd({'title':title},
					{
						'func': 'KVMovies',
						'status_line':'Категория: '+title,
						'url' : url
					})
		
		XBMCEnd()
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-kivikg.png'))

def KVMovies(params):
	try:
		XBMCItemAdd({'title':Colored(params['status_line'], 'bright')},
				{
					'func': 'KVCategories',
					'url': base_url
				})
		
		raw_html = HTML(params['url'])
		
		try:
			search = params['search']
			maxpage = None
		except:
			search = False
			try: 
				maxpage = int(re.compile('Результаты .+? из ([0-9]+?)</div>').findall(raw_html)[0]) / 20
				if(int(re.compile('Результаты .+? из ([0-9]+?)</div>').findall(raw_html)[0]) % 20 != 0):
					maxpage+=1
			except: maxpage = None
		
		if (maxpage != None):
			parsed = urlparse.urlparse(params['url'])
			try   : page = 1 if(int(urlparse.parse_qs(parsed.query)['limitstart'][0]) < 20) else (int(urlparse.parse_qs(parsed.query)['limitstart'][0]) / 20 + 1)
			except: page = 1

			XBMCItemAdd({'title':Colored('[ Перейти на страницу ]', 'opendialog')+' '+str(page)+' из '+str(maxpage)+' страниц', 'thumb':ImagePath('findpage.png')},
				{
					'func': 'KVPages',
					'status_line': params['status_line'],
					'maxpage':maxpage,
					'url' : params['url']
				})

			if (page < maxpage):
				catID = 'http://kivi.kg/index.php?option=com_virtuemart&category_id='+str(urlparse.parse_qs(parsed.query)['category_id'][0])+'&page=shop.browse&Itemid=1&limit=20&limitstart='+str(page*20)
				XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
						{
							'func': 'KVMovies',
							'status_line': params['status_line'],
							'maxpage':maxpage,
							'url' : catID
						})
		
		if(search == True):
			html = json.loads(raw_html)
			for movie in html['product']:
				try:
					title = movie['name']
					
					movie_html = BeautifulSoup(HTML(movie['ahref']))
					info = movie_html.findAll('table')[2]
					movie_thumb = info.a['href']
					movie_url = re.compile("'file': '(.+?)'").findall(info.text)[0]
					
					XBMCItemAdd({'title':title, 'thumb':movie_thumb}, {'url':movie_url+UserAgent}, False)
				except:
					Noty('Kivi!kg', 'Файл с ошибками пропущен', ImagePath('noty-kivikg.png'))
		else:
			html = BeautifulSoup(raw_html)
			for div in html.findAll('div', {'class':'browseProductContainer'}):
				url = div.div.a['href']
				title = div.div.a['title']
				
				movie_html = BeautifulSoup(HTML(base_url+url))
				info = movie_html.findAll('table')[2]
				movie_thumb = info.a['href']
				movie_url = re.compile("'file': '(.+?)'").findall(info.text)[0]

				XBMCItemAdd({'title':title.encode('utf-8'), 'thumb':movie_thumb}, {'url':movie_url+UserAgent}, False)
		XBMCEnd()
	except:
		Noty('Kivi!kg', 'Сервер недоступен', ImagePath('noty-kivikg.png'))

def KVSearch(params):
	keyboard = xbmc.Keyboard('','Kivi!kg: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		KVMovies({'url':'http://kivi.kg//modules/mod_search_vmproduct/ajax_search.php?search='+str(keyboard.getText())+'&catlimit=0&prolimit=20', 'search':True, 'status_line':'Результаты поиска по запросу: '+str(keyboard.getText())})

def KVPages(params):
    keyboard = xbmc.Keyboard('','Kivi!kg: Перейти на страницу', False)
    keyboard.doModal()
    
    if keyboard.isConfirmed():
			input = int(keyboard.getText())
			try:
				if(input > 0 and input <= params['maxpage']):
					parsed = urlparse.urlparse(params['url'])
					try:    params['url'] = 'http://kivi.kg/index.php?option=com_virtuemart&category_id='+urlparse.parse_qs(parsed.query)['category_id'][0]+'&page=shop.browse&Itemid=1&limit=20&limitstart='+str((input - 1) * 20)
					except: pass
			except: pass
				
			KVMovies(params)