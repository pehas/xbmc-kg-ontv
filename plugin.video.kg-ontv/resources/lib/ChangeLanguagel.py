import xbmc, xbmcgui, xbmcaddon
from site_onlinetvkgMy import *

ACTION_PREVIOUS_MENU = 10
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_NAV_BACK = 92

__addon__        = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
onlinetvkg_login    = __addon__.getSetting('onlinetvkg_login')
onlinetvkg_password = __addon__.getSetting('onlinetvkg_password')
onlinetvkg_language = __addon__.getSetting('onlinetvkg_language')
#playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
onlinetvkg_cookies = ''
try:
	conn = urllib2.urlopen(urllib2.Request('http://onlinetv.kg/Auth/Login', urlencode({'UserName':onlinetvkg_login, 'Password':onlinetvkg_password, 'RememberMe':'true'}), {'User-Agent':UserAgent[12:]}))
	onlinetvkg_cookies = conn.info().getheader('Set-Cookie')
except: pass

class MyClass(xbmcgui.WindowDialog):
  def __init__(self):
    self.addControl(xbmcgui.ControlImage(400,300,500,100, 'special://home/addons/plugin.video.kg-ontv/resources/media/background.png'))
    self.strActionInfo = xbmcgui.ControlLabel(450, 300, 450, 200, '', 'font14', 'F0FF00FF')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('Для выхода из меню нажмите НАЗАД')
    self.player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    self.playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    self.playListItem = self.playList[self.playList.getposition()]
    self.rusbutton = xbmcgui.ControlRadioButton(550, 340, 80, 40, 'Rus', font='font14')
    self.engbutton = xbmcgui.ControlRadioButton(650, 340, 80, 40, 'Eng', font='font14')
    self.addControl(self.rusbutton)
    self.addControl(self.engbutton)
    self.rusbutton.setSelected(True)
    self.setFocus(self.rusbutton)

  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK:
      self.close()
    if action == ACTION_MOVE_LEFT:
      self.rusbutton.setSelected(True)
      self.engbutton.setSelected(False)
      self.setFocus(self.rusbutton)
    if action == ACTION_MOVE_RIGHT:
      self.engbutton.setSelected(True)
      self.rusbutton.setSelected(False)
      self.setFocus(self.engbutton)

  def onControl(self, control):
    if control == self.engbutton:
       self.engbutton.setSelected(True)
       self.rusbutton.setSelected(False)
       url = self.GetUrlByCIdhannel({'channelID':self.playListItem.getProperty('channelID'),'lang':'eng'})
       self.player.pause()
       self.player.play(url,self.playListItem)
       self.close()
    elif (control == self.rusbutton):
         self.engbutton.setSelected(False)
         self.rusbutton.setSelected(True)
         url = self.GetUrlByCIdhannel({'channelID':self.playListItem.getProperty('channelID'),'lang':'rus'})
         self.player.pause()
         self.player.play(url,self.playListItem)
         self.close()

  def message(self, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(" My message title", message)


  def GetUrlByCIdhannel(self, params):
    #try:
        #Noty('sdfsd',params['transId'],'',3000)
        language = HTML('http://onlinetv.kg/XMLService/LanguagesByChannelId/' + params['channelID'])
        languageTree = ES.fromstring(language)
        for child in languageTree:
            if(child.attrib['name'] == params['lang']):
                return child.attrib['url']
        return languageTree[0].attrib['url']
    #except:
        #Noty('Online TV', 'Сервер недоступен')

mydisplay = MyClass()
mydisplay.doModal()
del mydisplay