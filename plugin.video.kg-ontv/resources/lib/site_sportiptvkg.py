#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, json, math
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__ = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
baseurl   = 'http://sport.iptv.kg/'
def SIKCategories(params):
	try:
		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'SIKSearch',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Новинки на Sport.IPTV.kg'},
			{
				'func': 'SIKMovies',
				'order': '0',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Лучшие по просмотрам'},
			{
				'func': 'SIKBestsellers',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Категория: Виды спорта'},
			{
				'func': 'SIKGenre',
				'url' : params['url']
			})
		XBMCEnd()
	except:
		Noty('Sport.IPTV.kg', 'Сервер недоступен', '')

def SIKBestsellers(params):
	try:
		html = HTML(params['url']+'api.php?format=ajax', {"action[0]":"Video.getBestsellers"}).encode('utf-8')
		data = json.loads(html)
		for item in data['js'][0]['response']['bestsellers']:
			for video in item['movies']:
				try:
					html = HTML(params['url']+'api.php?format=ajax', {'action[0]':'Video.getMovie','movie_id[0]':video['movie_id']})
					video_info = json.loads(html)
					if(len(video_info['js'][0]['response']['movie']['files']) == 1):
						XBMCItemAdd({'title':(Colored(video['name'], 'bold')+' [' + item['name'] + ']').encode('utf-8'), 'thumb':params['url']+video['cover'], 'duration':video_info['js'][0]['response']['movie']['files'][0]['metainfo']['playtime']}, {'url':(video_info['js'][0]['response']['movie']['files'][0]['path']).replace('/home/video/', 'http://sport.iptv.kg/')}, False)
					else:
						XBMCItemAdd({'title':(Colored(video['name'], 'bold')+' [' + item['name'] + ']').encode('utf-8'), 'thumb':params['url']+video['cover']},
							{
								'func': 'SIKSerial',
								'vid' : video['movie_id'],
								'url' : params['url']
							})
				except:
					Noty('Sport.IPTV.kg', 'Файл с ошибкой пропущен', '')
		XBMCEnd()
	except:
		Noty('Sport.IPTV.kg', 'Сервер недоступен', '')

def SIKSerial(params):
	try:
		html = HTML(params['url']+'api.php?format=ajax', {'action[0]':'Video.getMovie','movie_id[0]':params['vid']}).encode('utf-8')
		video_info = json.loads(html)
		l = video_info['js'][0]['response']['movie']['files']
		l.pop(0)
		for video in video_info['js'][0]['response']['movie']['files']:
			try:
				fanart = ''
				if(len(video['frames']) > 0):
					fanart = video['frames'][0]

					XBMCItemAdd({'title':(video_info['js'][0]['response']['movie']['name'] + ': ' + video['name']).encode('utf-8'), 'thumb':params['url']+video_info['js'][0]['response']['movie']['covers'][0]['thumbnail'], 'fanart':params['url']+fanart, 'duration':video['metainfo']['playtime']}, {'url':(video['path']).replace('/home/video/', 'http://sport.iptv.kg/')}, False)
			except:
				Noty('Sport.IPTV.kg', 'Файл с ошибкой пропущен', '')
		XBMCEnd()
	except:
		Noty('Sport.IPTV.kg', 'Сервер недоступен', '')


def SIKMovies(params):
	try:
		try   : order = params['order']
		except: order = '0'

		try   : offset = params['offset']
		except: offset = '0'

		try   : genreID = params['gid']
		except: genreID = None

		try   : search = params['search']
		except: search = False

		if genreID:
			html = HTML(params['url']+'api.php?format=ajax', {'action[0]':'Video.getCatalog', 'genre[0]':genreID, 'offset[0]':offset,'size[0]':'20','order[0]':'0'}).encode('utf-8')
		elif search:
			html = HTML(params['url']).encode('utf-8')
		else:
			html = HTML(params['url']+'api.php?format=ajax', {'action[0]':'Video.getCatalog','offset[0]':offset,'size[0]':'20','order[0]':order}).encode('utf-8')

		video_info = json.loads(html)['json'][0]['response'] if search == True else json.loads(html)['js'][0]['response']

		videos_array = video_info['movies']

		if len(videos_array) > 0:
			try:
				pagesTotal   = int(math.ceil(int(video_info['total'])/20+1))
				pagesCurrent = int(offset)/20+1
				XBMCItemAdd({'title':Colored('[ Перейти на страницу ]', 'opendialog', True) + ' '+str(pagesCurrent)+' из '+str(pagesTotal)+' страниц', 'thumb':ImagePath('findpage.png')},
					{
						'func'  : 'SIKPages',
						'search': search,
						'gid'   : genreID,
						'order' : order,
						'offset': offset,
						'url'   : params['url']
					})
				if pagesCurrent < pagesTotal:
					XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
						{
							'func'  : 'SIKMovies',
							'search': search,
							'gid'   : genreID,
							'order' : order,
							'offset': str(int(pagesCurrent) * 20),
							'url'   : params['url']
						})
			except: pass
		
			for video in videos_array:
				try:
					html = HTML(baseurl+'api.php?format=ajax', {'action[0]':'Video.getMovie','movie_id[0]':video['movie_id']}).encode('utf-8')
					video_info2 = json.loads(html)

					fanart = ''
					if(len(video_info2['js'][0]['response']['movie']['files'][0]['frames']) > 0):
						fanart = baseurl+video_info2['js'][0]['response']['movie']['files'][0]['frames'][0]
					
					try:    rating_IMBD = video['rating_imdb_value']
					except: rating_IMBD = '0'

					try:    genres = ', '.join(video_info2['js'][0]['response']['movie']['genres'])
					except: genres = 'жанр не найден'

					title = 'None'
					try:    title = (Colored(video['name'], 'bold')+' ['+genres+', ' + video['year'] + ']   IMDB: [COLOR F0F8AF84]'+rating_IMBD+'[/COLOR] ('+video['rating_imdb_count'] + ') КиноПоиск: [COLOR F0F8AF84]'.decode('utf-8')+video['rating_kinopoisk_value']+'[/COLOR] ('+video['rating_kinopoisk_count'] + ')').encode('utf-8')
					except: title = (Colored(video['name'], 'bold')+' ['+genres+', ' + video['year'] + ']').encode('utf-8')

					if len(video_info2['js'][0]['response']['movie']['files']) == 1:
						try:    duration = video_info2['js'][0]['response']['movie']['files'][0]['metainfo']['playtime']
						except: duration = ''

						XBMCItemAdd({'title':title, 'thumb':baseurl+video['cover'], 'fanart':fanart, 'year':video['year'], 'genre':genres, 'rating':rating_IMBD, 'duration':duration},
							{'url'  : (video_info2['js'][0]['response']['movie']['files'][0]['path']).replace('/home/video/', 'http://sport.iptv.kg/')}, False)
					else:
						XBMCItemAdd({'title':title, 'thumb':baseurl+video['cover'], 'fanart':fanart, 'year':video['year']},
							{
								'func': 'SIKSerial',
								'vid' : video['movie_id'],
								'url' : baseurl
							})
				except:
					Noty('Sport.IPTV.kg', 'Файл с ошибкой пропущен', '')
		else:
			Noty('Sport.IPTV.kg', 'Видео не найдено', '')
	except:
		Noty('Sport.IPTV.kg', 'Сервер недоступен', '')
	XBMCEnd()
	

def SIKGenre(params):
	try:
		html = HTML(params['url']+'api.php?format=ajax', {'action[0]':'Video.getGenres'}).encode('utf-8')
		genre_info = json.loads(html)

		for genre in genre_info['js'][0]['response']['genres']:
			XBMCItemAdd({'title':(genre['name']+' ('+genre['count']+')').encode('utf-8')},
				{
					'func': 'SIKMovies',
					'gid' : genre['id'],
					'url' : params['url']
				})
	except:
		Noty('Sport.IPTV.kg', 'Сервер недоступен', '')
	XBMCEnd()
	

def SIKSearch(params):
	keyboard = xbmc.Keyboard('','Sport.IPTV.kg: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		SIKMovies({'url':'http://sport.iptv.kg/suggestion.php?q='+str(keyboard.getText()), 'search':True})

def SIKPages(params):
    keyboard = xbmc.Keyboard('','Sport.IPTV.kg: Перейти на страницу', False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        try:    params['offset'] = (int(keyboard.getText()) - 1) * 20
        except: params['offset'] = '0'

        SIKMovies(params)