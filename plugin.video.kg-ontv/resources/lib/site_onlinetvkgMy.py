import urllib
import xbmc, xbmcplugin, xbmcaddon
import xml.etree.ElementTree as ES

from bs4 import BeautifulSoup
from Header import *

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
onlinetvkg_login    = __addon__.getSetting('onlinetvkg_login')
onlinetvkg_password = __addon__.getSetting('onlinetvkg_password')
onlinetvkg_language = __addon__.getSetting('onlinetvkg_language')
onlinetvkg_parentControlpassword = __addon__.getSetting('onlinetvkg_parentControlpassword')
baseurl = 'http://onlinetv.kg/'
onlinetvkg_cookies = ''

try:
	if(sys.argv[2].find('onlinetv.kg') > -1 ):
		conn = urllib2.urlopen(urllib2.Request('http://onlinetv.kg/Auth/Login', urlencode({'UserName':onlinetvkg_login, 'Password':onlinetvkg_password, 'RememberMe':'true'}), {'User-Agent':UserAgent[12:]}))
		onlinetvkg_cookies = conn.info().getheader('Set-Cookie')
except: pass

def OTVMyStartPage(params):
    XBMCItemAdd({'title':Colored('Просмотр ТВ', 'light', True)},
      {
          'func': 'OTVMyShowTV',
          'url' : params['url']
      })
    XBMCItemAdd({'title':'Поиск по жанрам'},
      {
          'func': 'OTVMyShowGenres',
          'url' : 'http://onlinetv.kg/XMLService/Genres'
      })
    XBMCItemAdd({'title':'Поиск передачи', 'thumb':ImagePath('find.png')},
			{
					'func': 'OTVMySearch',
					'url' : params['url']
			})
    XBMCEnd()

def OTVMyShowTV(params):
    try:
        groups = HTML(params['url'])
        tree = ES.fromstring(groups)
        for child in tree:
            XBMCItemAdd({'title':Colored(child.attrib['name'], 'light', True)},
            {
            'func': 'OTVMyShowCTVhannelsByGroup',
            'url' : 'http://onlinetv.kg/XMLService/GroupChannels/' + child.attrib['id'],
            'GroupId' : child.attrib['id']
            })
        XBMCEnd()
    except:
       Noty('Online TV', 'Сервер недоступен')

def OTVMyShowCTVhannelsByGroup(params):
    try:
        groups = HTML(params['url'])
        tree = ES.fromstring(groups)
        xbmc.executebuiltin("Action(Stop)")
        onlinetvplaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        onlinetvplaylist.clear()
        for child in tree:
            language = HTML('http://onlinetv.kg/XMLService/LanguagesByChannelId/' + child.attrib['id'])
            transmission = ES.fromstring(language)
            url = GetURLByLanguage(transmission)
            icon = ImagePath('onlinetv/'+child.attrib['id']+'.png')
            if (CheckParentControl(transmission)):
                addLinkPlaylist(onlinetvplaylist, {'title':child.attrib['name'],'url': url,'thumb':icon,'channelID':child.attrib['id']})
            #else:
                #Noty('Online TV', 'Введите пароль родительского контроля')
        xbmc.executebuiltin("ActivateWindow(VideoPlaylist)")
    except:
       Noty('Online TV', 'Сервер недоступен')

def OTVMyShowGenres(params):
    try:
        genres = HTML(params['url'])
        genrestree = ES.fromstring(genres)
        for child in genrestree:
            #Noty('asdf',child.attrib['name'])
            XBMCItemAdd({'title':Colored(child.attrib['name'], 'light', True)},
            {
            'func': 'OTVMyShowRecordsByGenre',
            'url' : 'http://onlinetv.kg/XMLService/TransmissionsByGenreId/' + child.attrib['id'] + '/1/12',
            'GenreId': child.attrib['id'],
            'Page' : 1
            })
        XBMCEnd()
    except :
       Noty('Online TV', 'Сервер недоступен')

def OTVMyShowRecordsByGenre(params):
    try:
        page = int(params['Page']) + 1
        records = HTML(params['url'])
        tree = ES.fromstring(records)
        #Noty('sfsdf',params['url'],'',30000)
        if int(tree.attrib['count']) == 0:
            Noty('Online TV','По данному запросу ничего не найдено')
        else:
            for child in tree:
                icon = ImagePath('onlinetv/'+child.attrib['id']+'.png')
                transmissionCount = child.attrib['transmissionsCount']
                date = Colored(child.attrib['date'] + ' ' + child.attrib['hour'] + ':' + child.attrib['minute'] , 'FF268789')
                description = Colored(child.attrib['description'], 'FF61a061')
                #transmissionRecords = Colored(str(' ( записей - ' + child.attrib['transmissionsCount'] + ')').decode('utf-8')).encode('utf-8')
                if int(child.attrib['transmissionsCount']) > 1:
                    url = 'http://onlinetv.kg/XMLService/TransmissionsByGenreGroupedTransmissionId/' + params['GenreId'] + '/' + child.attrib['id'] + '/1/100'
                    XBMCItemAdd({'title':Colored(date + ' | '+ child.attrib['name'], 'light', True) + Colored(' ( records - ' + child.attrib['transmissionsCount'] + ')', 'bright', True)  + ' | ' + description},
                    {
                    'func': 'OTVMyPlayRecords',
                    'url' : url,
                    'transmissionCount' : transmissionCount
                    })
                else:
                    language = HTML('http://onlinetv.kg/XMLService/LanguagesByTransmissionId/' + child.attrib['id'])
                    transmission = ES.fromstring(language)
                    url = GetURLByLanguage(transmission)
                    if (CheckParentControl(transmission)):
                        XBMCItemAdd({'title':Colored(date + ' | ' + child.attrib['name'], 'light', False) + Colored(' ( records - ' + child.attrib['transmissionsCount'] + ')', 'bright', True)  + ' | ' + description},
                        {
                         'url' : url,
                        }, False)
                    #else:
                        #Noty('Online TV', 'Введите пароль родительского контроля')

            #Noty('sfsdf',params['Page'],'',30000)
            if params['Page'] <> tree.attrib['count']:
                XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
                    {
                    'func': 'OTVMyShowRecordsByGenre',
                    'url' : 'http://onlinetv.kg/XMLService/TransmissionsByGenreId/' + params['GenreId'] + '/' + str(page) + '/12',
                    'GenreId': params['GenreId'],
                    'Page' : page
                    })
            XBMCEnd()
    except:
       Noty('Online TV', 'Сервер недоступен')

def OTVMyPlayRecords(params):
    try:
        records = HTML(params['url'])
        tree = ES.fromstring(records)
        #Noty('sfsdf',params['url'],'',30000)
        xbmc.executebuiltin("Action(Stop)")
        onlinetvplaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        onlinetvplaylist.clear()
        for child in tree:
            language = HTML('http://onlinetv.kg/XMLService/LanguagesByTransmissionId/' + child.attrib['id'])
            transmission = ES.fromstring(language)
            #Noty('sfsdf',child.attrib['id'],'',30000)
            url = GetURLByLanguage(transmission)
            icon = ImagePath('onlinetv/'+child.attrib['id']+'.png')
            if (CheckParentControl(transmission)):
                addLinkPlaylist(onlinetvplaylist, {'title':child.attrib['name'],'url': url,'thumb':icon})
            #else:
                #Noty('Online TV', 'Введите пароль родительского контроля')
        xbmc.executebuiltin("ActivateWindow(VideoPlaylist)")
    except:
       Noty('Online TV', 'Сервер недоступен')


def OTVMySearch(params):
	keyboard = xbmc.Keyboard('','Online TV: Поиск передачи', False)
	keyboard.doModal()
	if keyboard.isConfirmed():
		OTVMyVideos({'url':'http://onlinetv.kg/XMLService/TransmissionsSearch/' + urllib.quote(str(keyboard.getText())) + '/1/12', 'Page' : 1, 'SearchCondition': urllib.quote(str(keyboard.getText()))})

def OTVMyVideos(params):
    try:
        page = int(params['Page']) + 1
        records = HTML(params['url'])
        tree = ES.fromstring(records)
        #Noty('sfsdf',params['url'],'',30000)
        if int(tree.attrib['count']) == 0:
            Noty('Online TV','По данному запросу ничего не найдено')
        else:
            for child in tree:
                #icon = ImagePath('onlinetv/'+child.attrib['id']+'.png')
                transmissionCount = child.attrib['transmissionsCount']
                #date = Colored(child.attrib['date'] + ' ' + child.attrib['hour'] + ':' + child.attrib['minute'] , 'FF268789')
                description = Colored(child.attrib['description'], 'FF61a061')
                #transmissionRecords = Colored(str(' ( записей - ' + child.attrib['transmissionsCount'] + ')').decode('utf-8')).encode('utf-8')
                if int(child.attrib['transmissionsCount']) > 1:
                    url = 'http://onlinetv.kg/XMLService/TransmissionsByGroupedSearchTransmissionId/' +  child.attrib['id'] + '/1/100'
                    XBMCItemAdd({'title':Colored(child.attrib['name'], 'light', True) + Colored(' ( records - ' + child.attrib['transmissionsCount'] + ')', 'bright', True)  + ' | ' + description},
                    {
                    'func': 'OTVMyPlayRecords',
                    'url' : url,
                    'transmissionCount' : transmissionCount
                    })
                else:
                    language = HTML('http://onlinetv.kg/XMLService/LanguagesByTransmissionId/' + child.attrib['id'])
                    transmission = ES.fromstring(language)
                    url = GetURLByLanguage(transmission)
                    if (CheckParentControl(transmission)):
                        XBMCItemAdd({'title':Colored(child.attrib['name'], 'light', False) + Colored(' ( records - ' + child.attrib['transmissionsCount'] + ')', 'bright', True)  + ' | ' + description},
                        {
                         'url' : url,
                        }, False)
                    #else:
                       # Noty('Online TV', 'Введите пароль родительского контроля')

            #Noty('sfsdf',tree.attrib['count'],'',30000)
            if (params['Page'] <> tree.attrib['count']) and (int(tree.attrib['count']) <> 0):
                XBMCItemAdd({'title':Colored('[ Следующая страница ]', 'nextpage'), 'thumb':ImagePath('next.png')},
                    {
                    'func': 'OTVMyVideos',
                    'url' : 'http://onlinetv.kg/XMLService/TransmissionsSearch/' + params['SearchCondition'] + '/' + str(page) + '/12',
                    'SearchCondition': params['SearchCondition'],
                    'Page' :page
                    })
            XBMCEnd()
    except:
       Noty('Online TV', 'Видео не найдено')

def GetURLByLanguage(languageTree):
    try:
        HTML('http://onlinetv.kg/XMLService/CheckParentPIN/' + onlinetvkg_parentControlpassword)
        for child in languageTree:
            if(child.attrib['name'] == onlinetvkg_language):
                return child.attrib['url']
        return languageTree[0].attrib['url']
    except:
        return languageTree[0].attrib['url']

def CheckParentControl(channel):
    try:
        if ((channel.attrib['IsGenreAllowed'] == 'true' and channel.attrib['IsParentControlled'] == 'false')
        or (channel.attrib['IsGenreAllowed'] == 'true' and channel.attrib['IsParentControlled'] == 'true' and channel.attrib['IsParentPasswordEntered'] == 'true')):
            return True
    except:
        return False

def getstr():
    return 'asdfasdfasdf'





