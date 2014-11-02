import xbmc, xbmcgui, xbmcaddon
import time
from datetime import date
from datetime import timedelta
from site_onlinetvkgMy import *

ACTION_PREVIOUS_MENU = 10
ACTION_MOVE_DOWN = 4
ACTION_MOVE_UP = 3
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_NAV_BACK = 92

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
onlinetvkg_language = __addon__.getSetting('onlinetvkg_language')
#playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
onlinetvkg_login    = __addon__.getSetting('onlinetvkg_login')
onlinetvkg_password = __addon__.getSetting('onlinetvkg_password')
onlinetvkg_cookies = ''
try:
	conn = urllib2.urlopen(urllib2.Request('http://onlinetv.kg/Auth/Login', urlencode({'UserName':onlinetvkg_login, 'Password':onlinetvkg_password, 'RememberMe':'true'}), {'User-Agent':UserAgent[12:]}))
	onlinetvkg_cookies = conn.info().getheader('Set-Cookie')
except: pass

class MyClass(xbmcgui.WindowDialog):
  def __init__(self):
    self.date = date.today()
    self.addControl(xbmcgui.ControlImage(50,70,800,600, 'special://home/addons/plugin.video.kg-ontv/resources/media/background.png'))
    self.strActionInfo = xbmcgui.ControlLabel(250, 80, 450, 200, '', 'font14', 'F0FF00FF')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('Для выхода из меню нажмите НАЗАД')
    self.list = xbmcgui.ControlList(60, 150, 750, 500,'font14', 'FF11b500')
    self.addControl(self.list)
    self.previousDay = xbmcgui.ControlButton(105, 115, 250, 30, "Предыдущий день")
    self.addControl(self.previousDay)
    self.nextDay = xbmcgui.ControlButton(505, 115, 250, 30, "Следующий день")
    self.addControl(self.nextDay)
    self.player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    self.playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    self.playListItem = self.playList[self.playList.getposition()]
    self.GetTransmissionsByChannelId({'channelID':self.playListItem.getProperty('channelID')})
    self.setFocus(self.list)

  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK:
      self.close()
    if action == ACTION_MOVE_DOWN:
      self.setFocus(self.list)
      self.list.getSelectedItem().setLabel(Colored(self.list.getSelectedItem().getLabel(),'FF268789',True))
      position = self.list.getSelectedPosition() - 1
      self.list.getListItem(position).setLabel(Colored(self.list.getListItem(position).getLabel(),'FF268789',False))
    if action == ACTION_MOVE_UP:
      self.setFocus(self.list)
      self.list.getSelectedItem().setLabel(Colored(self.list.getSelectedItem().getLabel(),'FF268789',True))
      position = self.list.getSelectedPosition() + 1
      self.list.getListItem(position).setLabel(Colored(self.list.getListItem(position).getLabel(),'FF268789',False))
    if action == ACTION_MOVE_LEFT:
      self.setFocus(self.previousDay)
    if action == ACTION_MOVE_RIGHT:
      self.setFocus(self.nextDay)

  def onControl(self, control):
    if control == self.previousDay:
        self.list.reset()
        self.date = self.date - timedelta(days=1)
        self.GetTransmissionsByChannelId({'channelID':self.playListItem.getProperty('channelID')})
    if control == self.nextDay:
        self.list.reset()
        self.date = self.date + timedelta(days=1)
        self.GetTransmissionsByChannelId({'channelID':self.playListItem.getProperty('channelID')})
    if control == self.list:
      item = self.list.getSelectedItem()
      self.player.pause()
      url = self.GetUrlByTransmissionId({'transId':item.getProperty('transId')})
      self.player.play(url,item)
      self.close()

  def message(self, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(" My message title", message)

  def GetTransmissionsByChannelId(self,params):
    try:
        transmissionbyChannelId = HTML('http://onlinetv.kg/XMLService/TransmissionsByChannel/' + params['channelID'] + '/' + self.date.isoformat())
        tree = ES.fromstring(transmissionbyChannelId)

        for child in tree:
            date = Colored(child.attrib['date'] + ' ' + child.attrib['hour'] + ':' + child.attrib['minute'] , 'FF268789')
            description = Colored(child.attrib['description'], 'FF61a061')
            item = xbmcgui.ListItem(Colored(date + ' | ' + child.attrib['name'], 'light', False) + ' | ' + description)
            item.setInfo( type="Video", infoLabels={'Title':child.attrib['name']} )
            item.setProperty('transId',child.attrib['id'])
            item.setProperty('channelID',params['channelID'])
            self.list.addItem(item)
    except:
        Noty('Online TV','Сервер недоступен')

  def GetUrlByTransmissionId(self, params):
    try:
        language = HTML('http://onlinetv.kg/XMLService/LanguagesByTransmissionId/' + params['transId'])

        transmission = ES.fromstring(language)

        return GetURLByLanguage(transmission)
    except:
        Noty('Online TV', 'Сервер недоступен')

mydisplay = MyClass()
mydisplay.doModal()
del mydisplay