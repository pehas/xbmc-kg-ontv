#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,math,urllib2,uuid,time
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
baseurl = 'http://cinemaonline.kg/'
addurl = None
cookies = None

def getCookie(url, cookie_name, setcookie = ''):
	try:
		conn = urllib2.urlopen(urllib2.Request(url, None, {'Host':'cinemaonline.kg','User-Agent':UserAgent[12:],'Cookie':setcookie}))
		cookies = conn.info().getheader('Set-Cookie')
		for cookie in cookies.split('; '):
			cookie = cookie.split('=')
			name = cookie[0]
			value = cookie[1]
			if name == cookie_name:
					return str(value)
	except:
		return ''

if(sys.argv[2].find('cinemaonline.kg') > -1):
	cinema_phpsessid = 'PHPSESSID='+getCookie(baseurl,'PHPSESSID')
	cookies = cinema_phpsessid+'; '+'__utmp='+getCookie(baseurl+'cinema.png?'+str(int(time.time())),'__utmp',cinema_phpsessid)+';'

	phpsession = 'api.php?format=ajax&' + cinema_phpsessid + '&JsHttpRequest='+str(int(time.time()))+'-xml'

def COCategories(params):
	try:
		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'COSearch',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Бестселлеры'},
			{
				'func': 'COBestsellers',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Новинки на CinemaOnline'},
			{
				'func': 'COMovies',
				'order': '0',
				'url' : params['url']
			})
		XBMCItemAdd({'title':'Лучшие IMDB'},
			{
				'func' : 'COMovies',
				'order': '2',
				'url'  : params['url']
			})
		XBMCItemAdd({'title':'Лучшие КиноПоиск'},
			{
				'func' : 'COMovies',
				'order': '9',
				'url'  : params['url']
			})
		XBMCItemAdd({'title':'Жанры'},
			{
				'func': 'COGenre',
				'url' : params['url']
			})
		XBMCEnd()
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-cinemaonlinekg.png'))

def COBestsellers(params):
	try:
		html = HTML(params['url']+phpsession, {"action[0]":"Video.getBestsellers"}, cookies).encode('utf-8')
		data = json.loads(html)
		for item in data['js'][0]['response']['bestsellers']:

			for video in item['movies']:
				try:
					html = HTML(params['url']+phpsession, {'action[0]':'Video.getMovie','movie_id[0]':video['movie_id']}, cookies)
					video_info = json.loads(html)
					if(len(video_info['js'][0]['response']['movie']['files']) == 1):
						XBMCItemAdd({'title':(Colored(video['name'], 'bold')+' [' + item['name'] + ']').encode('utf-8'), 'thumb':params['url']+video['cover'], 'duration':video_info['js'][0]['response']['movie']['files'][0]['metainfo']['playtime']}, {'url':(video_info['js'][0]['response']['movie']['files'][0]['path']).replace('/home/video/', 'http://cinemaonline.kg:8080/')+UserAgent}, False)
					else:
						XBMCItemAdd({'title':(Colored(video['name'], 'bold')+' [' + item['name'] + ']').encode('utf-8'), 'thumb':params['url']+video['cover']},
							{
								'func': 'COSerial',
								'vid' : video['movie_id'],
								'url' : params['url']
							})
				except: pass
		XBMCEnd()
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-cinemaonlinekg.png'))

def COSerial(params):
	try:
		html = HTML(params['url']+phpsession, {'action[0]':'Video.getMovie','movie_id[0]':params['vid']}, cookies).encode('utf-8')
		video_info = json.loads(html)
		l = video_info['js'][0]['response']['movie']['files']
		l.pop(0)
		for video in video_info['js'][0]['response']['movie']['files']:
			fanart = ''
			if(len(video['frames']) > 0):
				fanart = video['frames'][0]

				XBMCItemAdd({'title':(video_info['js'][0]['response']['movie']['name'] + ': ' + video['name']).encode('utf-8'), 'thumb':params['url']+video_info['js'][0]['response']['movie']['covers'][0]['original'], 'fanart':params['url']+fanart, 'duration':video['metainfo']['playtime']}, {'url':(video['path']).replace('/home/video/', 'http://cinemaonline.kg:8080/')+UserAgent}, False)
		XBMCEnd()
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-cinemaonlinekg.png'))


def COMovies(params):
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
			html = HTML(params['url']+phpsession, {'action[0]':'Video.getCatalog', 'genre[0]':genreID, 'offset[0]':offset,'size[0]':'20','order[0]':'0'}, cookies).encode('utf-8')
		elif search:
			html = HTML(params['url']).encode('utf-8')
		else:
			html = HTML(params['url']+phpsession, {'action[0]':'Video.getCatalog','offset[0]':offset,'size[0]':'20','order[0]':order}, cookies).encode('utf-8')

		video_info = json.loads(html)['json'][0]['response'] if search == True else json.loads(html)['js'][0]['response']

		videos_array = video_info['movies']

		if len(videos_array) > 0:
			try:
				pagesTotal   = int(math.ceil(int(video_info['total'])/20+1))
				pagesCurrent = int(offset)/20+1
				XBMCItemAdd({'title':Colored('[ Перейти на страницу ]', 'opendialog', True) + ' '+str(pagesCurrent)+' из '+str(pagesTotal)+' страниц', 'thumb':ImagePath('findpage.png')},
					{
						'func'  : 'COPages',
						'search': search,
						'gid'   : genreID,
						'order' : order,
						'offset': offset,
						'url'   : params['url']
					})
				if pagesCurrent < pagesTotal:
					XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
						{
							'func'  : 'COMovies',
							'search': search,
							'gid'   : genreID,
							'order' : order,
							'offset': str(int(pagesCurrent) * 20),
							'url'   : params['url']
						})
			except: pass
		
			for video in videos_array:
				try:
					html = HTML(baseurl+phpsession, {'action[0]':'Video.getMovie','movie_id[0]':video['movie_id']},cookies).encode('utf-8')
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
						
						try:    plot = video_info2['js'][0]['response']['movie']['description']
						except: plot = ''

						XBMCItemAdd({'title':title, 'thumb':baseurl+video_info2['js'][0]['response']['movie']['covers'][0]['original'], 'fanart':fanart, 'year':video['year'], 'genre':genres, 'rating':rating_IMBD, 'duration':duration, 'plot':plot},
							{'url'  : (video_info2['js'][0]['response']['movie']['files'][0]['path']).replace('/home/video/', 'http://cinemaonline.kg:8080/')+UserAgent}, False)
					else:
						XBMCItemAdd({'title':title, 'thumb':baseurl+video['cover'], 'fanart':fanart, 'year':video['year']},
							{
								'func': 'COSerial',
								'vid' : video['movie_id'],
								'url' : baseurl
							})
				except:
					Noty('Cinema Online', 'Файл с ошибкой пропущен', ImagePath('noty-cinemaonlinekg.png'))
			XBMCEnd()
		else:
			Noty('Cinema Online', 'Видео не найдено', ImagePath('noty-cinemaonlinekg.png'))
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-cinemaonlinekg.png'))
	

def COGenre(params):
	try:
		html = HTML(params['url']+phpsession, {'action[0]':'Video.getGenres'}, cookies).encode('utf-8')
		genre_info = json.loads(html)

		for genre in genre_info['js'][0]['response']['genres']:
			XBMCItemAdd({'title':(genre['name']+' ('+genre['count']+')').encode('utf-8')},
				{
					'func': 'COMovies',
					'gid' : genre['id'],
					'url' : params['url']
				})
		XBMCEnd()
	except:
		Noty('Cinema Online', 'Сервер недоступен', ImagePath('noty-cinemaonlinekg.png'))
	

def COSearch(params):
	keyboard = xbmc.Keyboard('','Cinema Online: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		COMovies({'url':'http://cinemaonline.kg/suggestion.php?q='+str(keyboard.getText()), 'search':True})

def COPages(params):
    keyboard = xbmc.Keyboard('','Cinema Online: Перейти на страницу', False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        try:    params['offset'] = (int(keyboard.getText()) - 1) * 20
        except: params['offset'] = '0'

        COMovies(params)