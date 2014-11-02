#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import xbmc, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup
from Header import *

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
onlinetvkg_login    = __addon__.getSetting('onlinetvkg_login')
onlinetvkg_password = __addon__.getSetting('onlinetvkg_password')

def OTVStartPage(params):
	XBMCItemAdd({'title':Colored('Просмотр ТВ', 'light', True)},
		{
			'func': 'OTVShowTV',
			'url' : params['url'],
			'action' : 1
		})
	XBMCItemAdd({'title':'Поиск передачи', 'thumb':ImagePath('find.png')},
		{
			'func': 'OTVSearch',
			'url' : params['url']
		})
	XBMCItemAdd({'title':'Поиск по жанрам'},
		{
			'func': 'OTVSearchGenre',
			'url' : 'http://onlinetv.kg/TV/Genres'
		})
	XBMCEnd()

def OTVShowTV(params):
	try:
		onlinetv_cookie = HTML('http://onlinetv.kg/Auth/Login', {'UserName':onlinetvkg_login, 'Password':onlinetvkg_password, 'RememberMe':'true'})
		if not onlinetv_cookie or onlinetv_cookie == 'false':
			Noty('Online TV', 'Ошибка авторизации / Cервер недоступен', '', 5000)
		else:
			onlinetv_token = HTML(params['url']+'TV/GetNewTransmissionUID?')
			xbmc.executebuiltin("Action(Stop)")
			onlinetvplaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			onlinetvplaylist.clear()
			playlist = {'[Эфирные каналы]':{
							'РТР Планета':'57', 
							'ОРТ - Первый канал':'102', 
							'Время':'105', 
							'КТР':'109'},
						'[Познавательные]':{
							'Discovery Science':'1', #'Nat Geo Wild':'112', 
							'Телепутешествия':'teleputhd', 
							'Discovery Channel Russia':'55', 
							'National Geographic':'66', 
							'Виасат Эксплорер':'83', 
							'Виасат Хистори':'85', 
							'Телеканал Да Винчи':'94'},
						'[Детские]':{
							'Nickelodeon':'31', 
							'Карусель':'44', 
							'Детский':'79'},
						'[Развлекательные]':{
							'Телекафе':'104', 
							'Россия К':'71', 
							'Боорсок ТВ':'114', 
							'СТС':'116', 
							'Охота и Рыбалка':'118', 
							'Здоровое ТВ':'119'},
						'[Музыкальные]':{
							'Муз ТВ':'60', 
							'Ю':'61', 
							'Музыка первого':'106'},
						'[Кино]':{
							#'Кинохит':'6', 
							'Fox Life Russia':'73', 
							'Комедия ТВ':'72', 
							'Sony Entertainment TV':'75', 
							'TV 1000':'91', 
							'TV 1000 Action':'92', 
							'TV 1000 Русское Кино':'93', 
							'Sony Sci-Fi':'99', 
							'Fox Crime':'101', 
							'Дом кино':'103',
							#'ЕвроКино':'115',
							'ТВ ПРО':'124',
							'Киноплюс':'125',
							'Sony Turbo':'129'},
						'[Спортивные]':{
							'НТВ Футбол':'5', 
							'НТВ Наш футбол':'41', 
							'Спорт 1':'62', 
							'Спорт 2':'64', 
							'Eurosport 1':'35', 
							'Eurosport 2':'65', 
							'Боец':'58', 
							'Виасат Спорт':'89',
							'Сетанта Спорт':'122'},
						'[Авто]':{
							'Авто Плюс':'96',
							'Драйв':'117'},
						'[Природа]':{
							'Animal Planet Russia':'67', 
							'Виасат Нэйчер':'87',
							'Домашние Животные':'120'},
						'[Новостные]':{
							'Euronews':'9', 
							'Россия 24':'42', 
							'РБК ТВ':'80'}}
			for category in playlist:
				for channel in playlist[category]:
					channel_id = playlist[category][channel]
					ctitle = category + ' ' + Colored(channel, 'bold')
					icon = ImagePath('onlinetv/'+channel_id+'.png')
					if channel_id == 'teleputhd':
						addLinkPlaylist(onlinetvplaylist, {'title':ctitle, 'url':'http://onlinetv.kg:8090/', 'thumb':icon})
					else:
						addLinkPlaylist(onlinetvplaylist, {'title':ctitle, 'url':'http://stream.onlinetv.kg:8889/'+channel_id+'/'+onlinetv_token, 'thumb':icon})
			xbmc.executebuiltin("ActivateWindow(VideoPlaylist)")
			#xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(onlinetvplaylist)
	except:
		Noty('Online TV', 'Сервер недоступен')
	#XBMCEnd()

def OTVVideos(params):
	onlinetv_cookie = HTML('http://onlinetv.kg/Auth/Login', {'UserName':onlinetvkg_login, 'Password':onlinetvkg_password, 'RememberMe':'true'})
	if not onlinetv_cookie or onlinetv_cookie == 'false':
		Noty('Online TV', 'Ошибка авторизации / Cервер недоступен', '', 5000)
	else:
		onlinetv_token = HTML('http://onlinetv.kg/TV/GetNewTransmissionUID?')
		html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url']).replace('<br/>',' ')))

		try:    page = int(params['page'])
		except: page = 0

		current_page = page if page > 0 else 1
		try:
			pages_all = html.find('ul', attrs={'class':'pages'}).findAll('a')[-1].string
			XBMCItemAdd({'title':Colored('[ Перейти на страницу ]', 'opendialog') + ' ' + str(current_page) + ' из ' + str(pages_all) + ' страниц', 'thumb':ImagePath('findpage.png')},
				{
					'func': 'OTVSearchPage',
					'page': current_page,
					'url' : params['url']
				})

			if current_page < int(pages_all):
				current_page = (page + 1) if page > 0 else 2
				url = (params['url'] + '/' + str(current_page)) if page < 1 else params['url'][:(len(str(page)) * -1)] + str(current_page)

				XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
					{
						'func': 'OTVVideos',
						'page': current_page,
						'url' : url
					})
		except: pass

		video_list = html.find('div', attrs={'class':'results'}).findAll('a')
		if len(video_list) > 0:
			for a in video_list:
				url = str(a['href'])

				time = Colored(str(a.div.find('div', {'class':'time'}).string).decode('utf-8'), 'FF268789').encode('utf-8')
				description = Colored(str(a.div.find('div', {'class':'description'}).string).decode('utf-8'), 'FF61a061').encode('utf-8').replace('-', '').strip()
				
				if url.find('GenreGroupTransmissions') >= 0 or url.find('GroupedSearch') >= 0:
					name1 = str(a.div.find('div', {'class':'name'}))
					name1 = BeautifulSoup(name1.replace('<span>', '[COLOR FF00AA00] ').replace('</span>', '[/COLOR] ').strip())
					name = Colored(name1.div.string.encode('utf-8'), 'bold')
					
					XBMCItemAdd({'title': time + '  |  ' + name + '  |  ' + description},
						{
							'func': 'OTVVideos',
							'page': current_page,
							'url' : 'http://onlinetv.kg' + url
						})
				else:
					name = Colored(a.div.find('div', {'class':'name'}).string.title(), 'bold').encode('utf-8')
					url_re = re.compile('TV/VOD/(.+[0-9])').findall(url)[0]
					XBMCItemAdd({'title': time + '  |  ' + name + '  |  ' + description}, {'url' : 'http://vod.onlinetv.kg/FileUpload/' + onlinetv_token + '/rus/' + url_re + '.ts'}, False)
			XBMCEnd()
		else:
			Noty('Online TV', 'Видео не найдено')
	

def OTVSearchGenre(params):
	onlinetv_cookie = HTML('http://onlinetv.kg/Auth/Login', {'UserName':onlinetvkg_login, 'Password':onlinetvkg_password, 'RememberMe':'true'})
	if not onlinetv_cookie or onlinetv_cookie == 'false':
		Noty('Online TV', 'Ошибка авторизации / Cервер недоступен', '', 5000)
	else:
		html = BeautifulSoup(re.sub('\s+', ' ', HTML(params['url'])))

		for a in html.find('div', {'class':'results genres'}).findAll('a'):
			XBMCItemAdd({'title':a.div.div.string.encode('utf-8')},
				{
					'func': 'OTVVideos',
					'url' : 'http://onlinetv.kg'+a['href']
				})
		XBMCEnd()

def OTVSearch(params):
	keyboard = xbmc.Keyboard('','Online TV: Поиск передачи', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		OTVVideos({'url':'http://onlinetv.kg/TV/Search/' + urllib.quote(str(keyboard.getText()))})

def OTVSearchPage(params):
	keyboard = xbmc.Keyboard('','Online TV: Перейти на страницу', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		try:    enteredpage = int(keyboard.getText())
		except: enteredpage = 1

		try:    page = int(params['page'])
		except: page = 0

		current_page = (page + 1) if page > 0 else 2
		url = (params['url'] + '/' + str(enteredpage)) if page < 1 else params['url'][:(len(str(page)) * -1)] + str(enteredpage)

		OTVVideos({'url':url, 'page':enteredpage})