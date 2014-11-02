#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, sys
import xbmc, xbmcplugin, xbmcaddon
from Header            import *
from site_blivekg      import *
from site_obskg        import *
from site_tskg         import *
from site_nambamovies  import *
from site_nambaserials import *
from site_cinemaonline import *
from site_onlinetvkg   import *
from site_sportiptvkg  import *
from site_888kg        import *
from site_kivikg       import *
from site_onlinetvkgMy import *
from site_startvkg import *

if (__name__ == '__main__' ):
	_main()


def MainMenu(params):
	XBMCItemAdd({'title':'Билайв', 'thumb':ImagePath('blive-kg.png')},
		{
			'func': 'BLCategories',
			'url' : 'http://www.blive.kg/'
		})

	XBMCItemAdd({'title':'OBS.KG', 'thumb':ImagePath('obs-kg.png')},
		{
			'func': 'OBSCategories',
			'url' : 'http://obs.kg/'
		})

	XBMCItemAdd({'title':'TS.KG', 'thumb':ImagePath('ts-kg.png')},
		{
			'func': 'TSCategories',
			'url' : 'http://www.ts.kg/'
		})

	XBMCItemAdd({'title':'Namba.Кинозал', 'thumb':ImagePath('movie-namba-kg.png')},
		{
			'func': 'NMCategories',
			'url' : 'http://movie.namba.kg/'
		})

	XBMCItemAdd({'title':'Namba.Сериалы', 'thumb':ImagePath('movie-namba-kg.png')},
		{
			'func': 'NSCategories',
			'url' : 'http://serials.namba.kg/'
		})

	XBMCItemAdd({'title':'Online TV', 'thumb':ImagePath('onlinetv-kg.png')},
		{
			'func': 'OTVMyStartPage',
			'url' : 'http://onlinetv.kg/XMLService/Groups'
		})

	XBMCItemAdd({'title':'Cinema Online', 'thumb':ImagePath('cinemaonline-kg.png')},
		{
			'func': 'COCategories',
			'url' : 'http://cinemaonline.kg/'
		})

	XBMCItemAdd({'title':'Sport.IPTV.kg', 'thumb':ImagePath('sport-iptv-kg.png')},
		{
			'func': 'SIKCategories',
			'url' : 'http://sport.iptv.kg/'
		})

	XBMCItemAdd({'title':'Кинозал 888.kg', 'thumb':ImagePath('888-kg.png')},
		{
			'func': 'M8Categories',
			'url' : 'http://movies.888.kg/'
		})

	XBMCItemAdd({'title':'Kivi!kg - Фильмы онлайн', 'thumb':ImagePath('kivi-kg.png')},
		{
			'func': 'KVCategories',
			'url' : 'http://kivi.kg/'
		})
	
	XBMCItemAdd({'title':'StarTV.kg', 'thumb':ImagePath('startv-kg.png')},
		{
			'func': 'STVCategories'
		})

	XBMCItemAdd({'title':Colored('Настройки KG OnTV', 'opendialog')},
		{
			'func': 'run_settings',
		}, False)
		
		

	XBMCEnd()


def _params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param


def _main():
	params = _params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		MainMenu(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			Noty('Ошибка дополнения', 'Функция "%s" не найдена' % func, 2000)
		if pfunc: pfunc(params)