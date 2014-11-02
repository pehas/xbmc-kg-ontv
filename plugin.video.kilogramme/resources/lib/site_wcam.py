#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, json
from _header import *

BASE_NAME_SAIMA  = common.replaceHTMLCodes('&emsp;SAIMA TELECOM&emsp;live.saimanet.kg')
BASE_URL_SAIMA   = 'http://live.saimanet.kg/'

BASE_NAME_SMOTRI = common.replaceHTMLCodes('&emsp;SMOTRI.KG')
BASE_URL_SMOTRI  = 'http://www.smotri.kg/'

BASE_NAME_KT     = common.replaceHTMLCodes('&emsp;КыргызТелеком'.decode('utf-8'))
BASE_URL_KT      = 'http://kt.kg'

BASE_NAME  = 'Веб-камеры'
BASE_LABEL = 'wc'

@plugin.route('/site/' + BASE_LABEL)
def wc_index():
    item_list = get_cameras()
    
    items     = [{
        'label'       : item['name'],
        'path'        : item['url'],
        'thumbnail'   : item['icon'],
        'is_playable' : True
    } for item in item_list]
        
    return items





def get_cameras():
    items = []
    try:
        cache = plugin.get_storage(BASE_LABEL, TTL = 720)
        return cache['cameras']
    except:
        try:
            result = common.fetchPage({'link': BASE_URL_SAIMA})
            if result['status'] == 200:
                html = result['content']
                cameras_block = common.parseDOM(html, 'div', attrs = {'id': 'content'})
                cameras_block = common.parseDOM(cameras_block, 'div', attrs = {'class' : 'title'})
                
                cameras_name  = common.parseDOM(cameras_block, 'a')
                cameras_href  = common.parseDOM(cameras_block, 'a', ret = 'href')
                icon_parent   = common.parseDOM(html, 'a', attrs = {'id': 'logo'})
                icon          = common.parseDOM(icon_parent, 'img', ret = 'src')
                
                for i in range(0,len(cameras_name)):
                    try:
                        name = set_color(cameras_name[i], 'bold') + BASE_NAME_SAIMA
                        href = cameras_href[i]
                        
                        result = common.fetchPage({'link': BASE_URL_SAIMA + href[1:]})
                        if result['status'] == 200:
                            html = result['content']
                            url  = common.parseDOM(result['content'], 'a', attrs = {'id' : 'player'}, ret = 'href')[0]
                            
                            items.append({'name':common.replaceHTMLCodes( name ), 'url':url, 'icon':BASE_URL_SAIMA + icon[0][1:]})
                    except: pass
        except: pass
        try:
            result = common.fetchPage({'link': BASE_URL_SMOTRI})
            if result['status'] == 200:
                html = result['content']
                cameras_block = common.parseDOM(html, 'div', attrs = {'id': 'block-views-cameras-block'})
                cameras_name  = common.parseDOM(cameras_block, 'a')
                cameras_href  = common.parseDOM(cameras_block, 'a', ret = 'href')
                
                logo          = common.parseDOM(html, 'img ', attrs = {'alt': 'Главная'.decode('utf-8')}, ret = 'src')
                
                for i in range(0,len(cameras_name)):
                    try:
                        name = set_color(cameras_name[i], 'bold') + BASE_NAME_SMOTRI
                        href = cameras_href[i]
                        
                        result = common.fetchPage({'link': BASE_URL_SMOTRI + href[1:]})
                        if result['status'] == 200:
                            html = result['content']
                            
                            rtmp = re.compile('"vid","(.+?)"\);').findall(html)[0]
                            #icon = re.compile('"prev","(.+?)"\);').findall(html)[0]#BASE_URL_SMOTRI + icon[1:]
                                
                            items.append({'name':common.replaceHTMLCodes( name ), 'url':rtmp, 'icon':logo[0]})
                    except: pass
        except: pass

        try:
            result = common.fetchPage({'link': BASE_URL_KT + '/about_us/web-camera/'})
            if result['status'] == 200:
                html = result['content'].decode('cp1251')

                tabs = common.parseDOM(html, 'div', attrs = {'class': 'tabmenu'})
                li   = common.parseDOM(tabs, 'li')

                cameras_name = common.parseDOM(li, 'a')
                cameras_href = common.parseDOM(li, 'a', ret = 'href')

                icon  = 'http://kt.kg/bitrix/templates/ktnet_copy/images/logo.gif'

                for i in range(0,len(cameras_name)):
                    try:
                        name = set_color(cameras_name[i], 'bold') + BASE_NAME_KT
                        href = cameras_href[i]
                        
                        result = common.fetchPage({'link': BASE_URL_KT + href})
                        if result['status'] == 200:
                            html = result['content'].decode('cp1251')
                            rtmp = re.compile('netConnectionUrl: \'(.+?)\'').findall(html)[0] + '/mystream'
                            
                            items.append({'name':common.replaceHTMLCodes( name ), 'url':rtmp, 'icon':icon})
                    except: pass
        except: pass
        
    cache['channels'] = items
    return items