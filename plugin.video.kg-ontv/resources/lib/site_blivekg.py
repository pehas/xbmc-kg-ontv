#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
blivekg_login    = __addon__.getSetting('blivekg_login')
blivekg_password = __addon__.getSetting('blivekg_password')
base_url = 'http://blive.kg/'

def checkSerial(names, needle):
	for a in names:
		if needle == a['url']:
			return True
	return False

def BLCategories(params):
	try:
		html = BeautifulSoup(HTML(params['url'], {'L':blivekg_login, 'P':blivekg_password}))

		XBMCItemAdd({'title':Colored('[ Поиск ]', 'opendialog', True), 'thumb':ImagePath('find.png')},
			{
				'func': 'BLSearch',
				'url' : params['url']
			})


		for category in html.find('div', attrs={'class':'master-sprite spriteCAT'}).parent.parent.findAll('div',attrs={'style':'width:170px;float:left;'}):
			title = Colored(category.a.string[2:], 'bold') + ' (' + category.nextSibling.string + ')' if category.nextSibling.string != '&nbsp;' else Colored(category.a.string[2:], 'bold')
			if category.a['href'] == '/tvserials/' or category.a['href'] == '/animeserials/':
				title = Colored(title, 'FF00CC00')

				XBMCItemAdd({'title': title.encode('utf-8')},
					{
						'func': 'BLVideosSerials',
						'url' : 'http://www.blive.kg'+category.a['href']
					})
			else:
				XBMCItemAdd({'title': title.encode('utf-8')},
					{
						'func': 'BLVideos',
						'status_line':'Категория: '+Colored(category.a.string[2:].encode('utf-8'), 'bold'),
						'url' : 'http://www.blive.kg'+category.a['href']
					})
		XBMCEnd()
	except:
		Noty('Билайв', 'Сервер недоступен', ImagePath('noty-blivekg.png'))

def BLVideos(params):
	try:
		XBMCItemAdd({'title':Colored(params['status_line'], 'bright')},
				{
					'func': 'BLCategories',
					'url' : 'http://www.blive.kg/'
				})
		
		try:
			html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url'], {'L':blivekg_login, 'P':blivekg_password, 'S':params['search']})))
		except:
			html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url'], {'L':blivekg_login, 'P':blivekg_password})))

		try:
			next = html.find('a', text=' &gt;&gt; ').parent
			XBMCItemAdd({'title':Colored('[ Следующие ' + next['title'].encode('utf-8') + ' ]', 'nextpage'), 'thumb':ImagePath('next.png')},
				{
					'func': 'BLVideos',
					'status_line':params['status_line'],
					'url' : 'http://www.blive.kg'+next['href']
				})
		except: pass

		videolist = html.findAll('div', attrs={'class':'vcell1 '})
		if len(videolist) > 0:
			for video in videolist:
				try:
					html = re.sub('\s+', ' ', HTML('http://www.blive.kg' + video.find('div', attrs={'class':'vcell1name'}).a['href']))
					src = re.compile(', {url:"(.+?)", autoPlay: false}').findall(BeautifulSoup(html).find('table', attrs={'class':'videotable'}).find('script', attrs={'src': None}).string)[0]
					size = re.compile('<p><i>Размер :</i> (.+?)\; <a').findall(html.decode('windows-1251').encode('utf-8'))[0].split(' ')
					try:
						if size[1] == 'Мб':
							size = int(float(size[0]) * 1024 * 1024)
					except:
						size = 0
					duration = video.find('span', {'class':'timevideo'}).span.string
					XBMCItemAdd({'title':video.find('div', attrs={'class':'vcell1name'}).a.string.encode('utf-8'), 'thumb':video.a.img['src'], 'size':size, 'duration':duration}, {'url' : src}, False)
				except: 
					Noty('Билайв', 'Файл с ошибкой пропущен', ImagePath('noty-blivekg.png'))
			XBMCEnd()
		else:
			Noty('Билайв', 'Видео не найдено', ImagePath('noty-blivekg.png'))
	except:
		Noty('Билайв', 'Сервер недоступен', ImagePath('noty-blivekg.png'))
	

serials = []
def BLVideosSerials(params):
	try:
		html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url'])))

		videolist = html.find('table', {'class':'videotable'}).table.findAll('a')
		if len(videolist) > 0:
			for a in videolist:
				XBMCItemAdd({'title': a['title'].encode('utf-8')},
					{
						'func': 'BLVideosEpisodes',
						'url' : 'http://www.blive.kg'+a['href']
					})
		else:
			Noty('Билайв', 'Видео не найдено', ImagePath('noty-blivekg.png'))
		XBMCEnd()
	except:
		Noty('Билайв', 'Сервер недоступен', ImagePath('noty-blivekg.png'))
	

def BLVideosEpisodes(params):
	try:
		html = BeautifulSoup(HTML(params['url']))

		videolist = html.find('div', {'class':'numline2 numline2-long'}).findAll('a')
		thumb = html.find('div', {'class':'serialimg'}).img['src']
		if len(videolist) > 0:
			title = html.find('div', {'class':'serial'}).h2.string
			#seasonNum = re.compile(': (.+?)<b').findall(str(video.h3))[0]
			for video in videolist:
				html = re.sub('\s+', ' ', HTML('http://www.blive.kg' + video['href']))
				src = re.compile(', {url:"(.+?)", autoPlay: false}').findall(str(BeautifulSoup(html).find('table', attrs={'class':'videotable'}).find('script', attrs={'src': None}).string))[0]
				size = re.compile('<p><i>Размер :</i> (.+?)\; <a').findall(html.decode('windows-1251').encode('utf-8'))[0].split(' ')

				XBMCItemAdd({'title':(title + ' [Episode: ' + video.string + ']'), 'thumb':thumb}, {'url' : src}, False)
			XBMCEnd()
		else:
			Noty('Билайв', 'Видео не найдено', ImagePath('noty-blivekg.png'))
	except:
		Noty('Билайв', 'Сервер недоступен', ImagePath('noty-blivekg.png'))
	

def BLSearch(params):
	keyboard = xbmc.Keyboard('','Билайв: Что ищем?', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		title = keyboard.getText().decode('utf-8').encode('windows-1251')
		BLVideos({'url':params['url'], 'search':title, 'status_line':'Результаты поиска по запросу: ' + Colored(keyboard.getText(), 'bold')})