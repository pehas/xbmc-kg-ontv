#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, urllib
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
obskg_quality    = __addon__.getSetting('obskg_quality')

def OBSCategories(params):
	try:
		html = BeautifulSoup(HTML(params['url']))

		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'OBSSearch',
				'url' : params['url']
			})

		for category in html.find('ul', attrs={'id':'categories'}).findAll('li'):
			category_link = category.find('a')
			category_count = category.find('span', attrs={'class':'count'})
			try:    title = Colored(category_link.string, 'bold') + ' ' + category_count.string + ' ' + Colored(category.find('span', attrs={'class':'new'}).string, 'light')
			except: title = Colored(category_link.string, 'bold') + ' ' + category_count.string

			if(category_link['href'] != 'http://ts.kg'):
				XBMCItemAdd({'title': title.encode('utf-8')},
				{
					'func': 'OBSVideos',
					'url' : params['url']+category_link['href']
				})
		XBMCEnd()
	except:
		Noty('OBS.KG', 'Сервер недоступен', ImagePath('noty-obskg.png'))
	

def OBSVideos(params):
	try:
		html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url'])))

		try:
			next = html.find('p', attrs={'class':'pagination'}).find('a', attrs={'rel':'next'})
			XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
				{
					'func': 'OBSVideos',
					'url' : 'http://obs.kg' + next['href']
				})
		except: pass

		try:    videolists = html.findAll('ul', attrs={'class':'video-list'})[1].findAll('li')
		except: videolists = html.findAll('ul', attrs={'class':'video-list'})[0].findAll('li')

		if len(videolists) > 0:
			for video in videolists:
				try:
					duration = video.find('div', {'class':'length'}).string.strip()

					try:    video_thumb = re.compile('\'(.+?)\'').findall(video.find('a', attrs={'class':'flash-holder'})['style'])[0]
					except: video_thumb = ''

					video_link = video.find('div', attrs={'class':'video-item-descr'}).find('a')
					video_title = re.sub('\s+', ' ', video_link.string)

					html = BeautifulSoup(re.sub('\s+', ' ', HTML('http://obs.kg'+video_link['href'])))

					if obskg_quality == 'true':
						#Высокое качество
						try:
							video_url = re.compile('"playlist":(.+?)}else{').findall(html.find('div', attrs={'class':'video'}).find('script', attrs={'src': None}).string)[0]
							video_info = json.loads(video_url[:-4])
							maxbit = video_info[1]['bitrates'][0]['bitrate']
							for video in video_info[1]['bitrates']:
								if video['bitrate'] > maxbit:
									maxbit = 'http://sec1.obs.kg/' + video['url']

								XBMCItemAdd({'title':video_title.strip().encode('utf-8'), 'thumb':video_thumb, 'duration':duration}, {'url': maxbit}, False)
						except:
							video_url = re.compile('src="(.+?)" type=').findall(html.find('div', attrs={'class':'video'}).find('script', attrs={'src': None}).string)[0]
							XBMCItemAdd({'title':video_title.strip().encode('utf-8'), 'thumb':video_thumb, 'duration':duration}, {'url': video_url}, False)
					else:
						#Низкое качество
						video_url = re.compile('src="(.+?)" type=').findall(html.find('div', attrs={'class':'video'}).find('script', attrs={'src': None}).string)[0]
						XBMCItemAdd({'title':video_title.strip().encode('utf-8'), 'thumb':video_thumb, 'duration':duration}, {'url': video_url}, False)
				except:
					Noty('OBS.KG', 'Файл с ошибкой пропущен', ImagePath('noty-obskg.png'))
			XBMCEnd()
		else:
			Noty('OBS.KG', 'Видео не найдено', ImagePath('noty-obskg.png'))
	except:
		Noty('OBS.KG', 'Сервер недоступен', ImagePath('noty-obskg.png'))

def OBSSearch(params):
	keyboard = xbmc.Keyboard('','OBS.KG: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		OBSVideos({'url':'http://obs.kg/browse/videos/?q='+urllib.quote(keyboard.getText())})