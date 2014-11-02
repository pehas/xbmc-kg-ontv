#!/usr/bin/python
# -*- coding: utf-8 -*-

from Header import *
base_url = 'http://startv.kg'

def STVCategories(param):
	XBMCItemAdd({'title':'Europa Plus TV', 'thumb': ImagePath('onlinetv/europaplustv.png')}, {'url':base_url+'/hls/provider/provider_europe.m3u8'}, False)
	XBMCItemAdd({'title':'Спорт 2', 'thumb': ImagePath('onlinetv/sport2.png')}, {'url':base_url+'/hls/provider/provider_sport.m3u8'}, False)
	XBMCItemAdd({'title':'Наука 2.0', 'thumb': ImagePath('onlinetv/nauka2.0.png')}, {'url':base_url+'/hls/provider/provider_nauka.m3u8'}, False)
	XBMCItemAdd({'title':'Nickelodeon', 'thumb': ImagePath('onlinetv/nickelodeon.png')}, {'url':base_url+'/hls/provider/provider_nickelodeon.m3u8'}, False)
	XBMCItemAdd({'title':'ЕвроКино', 'thumb': ImagePath('onlinetv/eurokino.png')}, {'url':base_url+'/hls/provider/provider_eurokino.m3u8'}, False)
	XBMCEnd()