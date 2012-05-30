#!/usr/bin/env python
import xbmc, xbmcgui, xbmcaddon, simplejson, os, sys, itertools, math
import xml.etree.ElementTree as et
from operator import itemgetter

__settings__    = xbmcaddon.Addon(id='script.xbmal')
__cwd__         = __settings__.getAddonInfo('path')
__icon__        = os.path.join(__cwd__, "icon.png")
__configFile__  = xbmc.translatePath('special://profile/addon_data/script.xbmal/config.xml')
__scriptname__	= "XBMAL"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join(__cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import myanimelist, xbmal

class MAL():
	def __init__(self):
		self.config = xbmal.XML()
		self.server = xbmal.server()
		self.output = xbmal.output()

	def fullUpdate(self):
		""" Performs a full update of MAL listings """
		self.output.notify(__settings__.getLocalizedString(300))
		showCount = 0;
		completed = self.config.parseConfig()
		#Get current MAL list (dictionary of dictionaries)
		malList = a.list()
		malListIDs = malList.keys()
		tvshows = self.server.getXBMCshows()		
		for tvshow in tvshows:
			seasons = self.server.getXBMCseasons(tvshow)
			for season in seasons:
				if season[0]['season'] == 0:
					continue #Don't do "season 0"
				malID = self.config.showInConfig(season[0]['tvshowid'], season[0]['season'])
				if (malID == -1 or malID == '%skip%' or malID == False):
					continue #move on...
				malID = int(malID)
				count = 0
				xbmc.log(str(season), xbmc.LOGNOTICE)
				for episode in season:
					if(episode['playcount'] != 0 and episode['label'][0] != 'S'):
						count = count + 1
				if malID in malListIDs:
					if malList[malID]['episodes'] is not None:
						epCount = int(malList[malID]['episodes'])
					else:
						epCount = 0
				else:
					details = a.details(malID)
					if details[u'episodes'] is not None:
						epCount = int(details[u'episodes'])
					else:
						epCount = 0
				if malID in malListIDs:
					if(malList[malID]['watched_status'] == u'watching' or malList[malID]['watched_status'] == u'plan to watch'):
						if count == epCount and epCount != 0:
							self.output.log(malList[malID]['title'] + " " + __settings__.getLocalizedString(302), xbmc.LOGNOTICE)
							a.update(malID, {'status':'completed', 'episodes':count, 'score':malList[malID]['score']})
							showCount = showCount + 1
						elif (count != 0 and (epCount == 0 or epCount > count)):
							self.output.log(malList[malID]['title'] + " " + __settings__.getLocalizedString(303) + " " + str(count), xbmc.LOGNOTICE)
							a.update(malID, {'status':'watching', 'episodes':count, 'score':malList[malID]['score']})
							showCount = showCount + 1
				else:
					if count == epCount and epCount != 0:
						self.output.log(details['title'] + " " + __settings__.getLocalizedString(302), xbmc.LOGNOTICE)
						a.add({'anime_id':malID, 'status':'completed', 'episodes':count})
						showCount = showCount + 1
					elif (count != 0 and (epCount == 0 or epCount > count)):
						self.output.log(details['title'] + " " + __settings__.getLocalizedString(303) + " " + str(count), xbmc.LOGNOTICE)
						a.add({'anime_id':malID, 'status':'watching', 'episodes':count})
						showCount = showCount + 1
					elif count == 0:
						self.output.log(details['title'] + " " + __settings__.getLocalizedString(304), xbmc.LOGNOTICE)
						a.add({'anime_id':malID, 'status':'plan to watch', 'episodes':count})
						showCount = showCount + 1
		self.output.notify(str(showCount) + " " + __settings__.getLocalizedString(301))
				

class XBMCPlayer( xbmc.Player ):
	def __init__(self, *args):
		xbmc.Player.__init__(self)
		self.wasVideo = False

	def onPlayBackEnded( self ):
		if self.wasVideo:
			mal = MAL()
			mal.fullUpdate()

	def onPlayBackStopped( self ):
		if self.wasVideo:
			mal = MAL()
			mal.fullUpdate()
	
	def onPlayBackStarted( self ):
		self.wasVideo = False
		if self.isPlayingVideo():
			self.wasVideo = True

	def onPlayBackResumed( self ):
		self.wasVideo = False
		if self.isPlayingVideo():
			self.wasVideo = True

#class XBMCMonitor( xbmc.Monitor ):
#	def __init__(self, *args):
#		pass

#	def onDatabaseUpdated(self, database):
#		xbmc.log("### [%s] - %s" %(__scriptname__,"Database Updated, Updating..."), level=xbmc.LOGNOTICE)
#		mal = MAL()
#		mal.fullUpdate(__configFile__)

#Entry point
player = XBMCPlayer()
#monitor = XBMCMonitor()
mal = MAL()
callmal = xbmal.MAL()
a = callmal.a
while not xbmc.abortRequested:
	if (a != False):
		xbmc.sleep(100)
	else:
		trys = 0
		if (trys <= 5) : #Only want to try 6 times, i.e., for half an hour.
			xbmc.sleep(1000 * 60 * 5) #Wait for 5 minutes before trying again
			callmal = xbmal.MAL()
			a = callmal.a
			trys = trys + 1 
		else:
			break #If it's been half an hour with no updates, break, as the user probably isn't going to update their credentials now.
