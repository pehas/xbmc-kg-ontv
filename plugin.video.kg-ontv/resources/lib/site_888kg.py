#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, json, math
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__ = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
baseurl   = 'http://cinemaonline.kg/'
def M8Categories(params):
	try:
		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'M8Search',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Топ-25'},
			{
				'func': 'M8Top',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Жанры'},
			{
				'func': 'M8Genre',
				'url' : params['url']
			})
		XBMCEnd()
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-cinemaonlinekg.png'))

def M8Top(params):
	try:
		html = BeautifulSoup(HTML(params['url']))
		for li in html.find('ul', {'class':'carousel'}).findAll('li'):
			movie = BeautifulSoup(HTML(li.a['href']))
			thumb = movie.find('a', {'onclick':'return hs.expand(this)'})['href']
			sources = movie.findAll('source')
			count = len(sources)
			if(count > 2):
				i = 1
				while(i < count):
					i += 1
					XBMCItemAdd({'title':(li.img['alt'] + ' [Файл '.decode('utf-8') + str(i-1) + ']').encode('utf-8'), 'thumb':thumb}, {'url':sources[i-1]['src']}, False)
			elif(count == 2):
				XBMCItemAdd({'title':(li.img['alt']).encode('utf-8'), 'thumb':thumb}, {'url':sources[1]['src']}, False)
			else:
				XBMCItemAdd({'title':(li.img['alt']).encode('utf-8'), 'thumb':thumb}, {'url':sources[0]['src']}, False)

		XBMCEnd()
	except:
		Noty('Кинозал 888.kg', 'Сервер недоступен', ImagePath('noty-888kg.png'))

def M8Genre(params):
	try:
		current_page = params['current_page'] if ('current_page' in params) else 1

		html = BeautifulSoup(HTML(params['url']))
		for genre in html.find('div', {'class':'s-block-content'}).findAll('a'):
			XBMCItemAdd({'title':genre.string},
				{
					'func': 'M8Movies',
					'url' : 'http://movies.888.kg'+genre['href']+'/page/1/',
					'current_page': current_page
				})
		XBMCEnd()
	except:
		Noty('Кинозал 888.kg', 'Сервер недоступен', ImagePath('noty-888kg.png'))

def M8Movies(params):
	try:
		html = BeautifulSoup(HTML(params['url']))

		current_page = int(params['current_page']) if ('current_page' in params) else 1
		try:
			nav = html.find('div', {'class':'navigation'}).findChildren()
			pagesTotal   = int(nav[-2].string)
			XBMCItemAdd({'title':Colored('[ Перейти на страницу ]', 'opendialog', True) + ' '+str(current_page)+' из '+str(pagesTotal)+' страниц', 'thumb':ImagePath('findpage.png')},
				{
					'func': 'M8Pages',
					'url' : params['url']
				})
			if current_page < pagesTotal:
				last_slash = params['url'][:-1].rfind('/')
				XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
					{
						'func': 'M8Movies',
						'url' : params['url'][:last_slash+1]+str(current_page + 1)+'/',
						'current_page' : current_page + 1
					})
		except: pass

		for li in html.find('td', {'class':'td-for-content'}).findAll('div', {'class':'short-block'}):
			movie = BeautifulSoup(HTML(li.a['href']))
			thumb = movie.find('a', {'onclick':'return hs.expand(this)'})['href']
			sources = movie.findAll('source')
			count = len(sources)
			if(count > 2):
				i = 1
				while(i < count):
					i += 1
					XBMCItemAdd({'title':(li.img['alt'] + ' [Файл '.decode('utf-8') + str(i-1) + ']').encode('utf-8'), 'thumb':thumb}, {'url':sources[i-1]['src']}, False)
			elif(count == 2):
				XBMCItemAdd({'title':(li.img['alt']).encode('utf-8'), 'thumb':thumb}, {'url':sources[1]['src']}, False)
			else:
				XBMCItemAdd({'title':(li.img['alt']).encode('utf-8'), 'thumb':thumb}, {'url':sources[0]['src']}, False)

		XBMCEnd()
	except:
		Noty('Кинозал 888.kg', 'Сервер недоступен', ImagePath('noty-888kg.png'))

def M8Search(params):
	keyboard = xbmc.Keyboard('','Кинозал 888.kg: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		url = 'http://movies.888.kg/engine/ajax/search.php'
		try:
			html = BeautifulSoup(HTML(url,{'query':keyboard.getText()}))
			links = html.findAll('a')
			if(len(links) > 0):
				for li in html.findAll('a'):
					movie = BeautifulSoup(HTML(li['href']))
					thumb = movie.find('a', {'onclick':'return hs.expand(this)'})['href']
					sources = movie.findAll('source')
					count = len(sources)
					if(count > 2):
						i = 1
						while(i < count):
							i += 1
							XBMCItemAdd({'title':(li.span.string + ' [Файл '.decode('utf-8') + str(i-1) + ']').encode('utf-8'), 'thumb':thumb}, {'url':sources[i-1]['src']}, False)
					elif(count == 2):
						XBMCItemAdd({'title':(li.span.string).encode('utf-8'), 'thumb':thumb}, {'url':sources[1]['src']}, False)
					else:
						XBMCItemAdd({'title':(li.span.string).encode('utf-8'), 'thumb':thumb}, {'url':sources[0]['src']}, False)
				XBMCEnd()
			else:
				Noty('Кинозал 888.kg', 'Поиск не дал результатов', ImagePath('noty-888kg.png'))
		except:
			Noty('Кинозал 888.kg', 'Поиск не дал результатов', ImagePath('noty-888kg.png'))
			M8Categories(params)

def M8Pages(params):
	keyboard = xbmc.Keyboard('','Кинозал 888.kg: Перейти на страницу', False)
	keyboard.doModal()
	last_slash = params['url'][:-1].rfind('/')
	if keyboard.isConfirmed():
		params['url'] = params['url'][:last_slash+1]+str(int(keyboard.getText()))+'/'
		params['current_page'] = int(keyboard.getText())
		M8Movies(params)