#!/usr/bin/env python
import xbmc, xbmcgui, xbmcaddon, simplejson, os, sys, itertools, math
import xml.etree.ElementTree as et
from operator import itemgetter

__settings__    = xbmcaddon.Addon(id='script.service.xbmal')
__cwd__         = __settings__.getAddonInfo('path')
__icon__        = os.path.join(__cwd__, "icon.png")
__configFile__  = xbmc.translatePath('special://profile/addon_data/script.service.xbmal/config.xml')
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
		if malList == False:	
			self.output.notify(__settings__.getLocalizedString(202))
			return False
		malListIDs = malList.keys()
		#Get all of the seasons of all of the shows in XBMC in a nice list.
		seasons = [y for x in self.server.getXBMCshows() for y in self.server.getXBMCseasons(x)]
		for season in seasons:
			if season[0]['season'] == 0:
				continue #Don't do "season 0"
			malID = self.config.showInConfig(season[0]['tvshowid'], season[0]['season'])
			if (malID == -1 or malID == '%skip%' or malID == False):
				continue #invalid mal id, asked to skip, or no mal id. Carry on...
			malID = int(malID)
			count = 0
			#xbmc.log(str(season), xbmc.LOGNOTICE)
			#Get number of watched episodes in XBMC.
			for episode in season:
				if(episode['playcount'] != 0 and episode['label'][0] != 'S'):
					count = count + 1
			if malID in malListIDs:
				#If we have the mal id already, get the total number of episodes
				epCount = int(malList[malID]['episodes']) if malList[malID]['episodes'] is not None else 0
				#and the number we have watched.
				malCount = int(malList[malID]['watched_episodes']) if malList[malID]['watched_episodes'] is not None else 0

				if(malList[malID]['watched_status'] == u'watching' or malList[malID]['watched_status'] == u'plan to watch'):
					if count == epCount and epCount != 0:
						#If we have the same number of episodes watched as the total number of episodes, and that number isn't 0, mark as completed.
						#XBMC Log can't handle unicode, need workaround
						self.output.log(malList[malID]['title'].encode('ascii','ignore') + " " + __settings__.getLocalizedString(302), xbmc.LOGNOTICE)
						if a.update(malID, {'status':'completed', 'episodes':count, 'score':malList[malID]['score']}) == False:
							self.output.notify(__settings__.getLocalizedString(202))
							return False
						showCount = showCount + 1
					elif (count != 0 and (epCount == 0 or epCount > count) and malCount < count):
						#If we have watched at least 1 episodes and the number of episodes is unknown or greater than the number we have watched, and the number we have watched on mal is less than the number we have watched on XBMC,
						#update the number.
						self.output.log(malList[malID]['title'].encode('ascii', 'ignore') + " " + __settings__.getLocalizedString(303) + " " + str(count), xbmc.LOGNOTICE)
						if a.update(malID, {'status':'watching', 'episodes':count, 'score':malList[malID]['score']}) == False:
							self.output.notify(__settings__.getLocalizedString(202))
							return False
						showCount = showCount + 1

			else:
				#If we don't have the mal ID, get details about the series.
				details = a.details(malID)
				if details == False:
					#If there are none, error and return
					self.output.notify(__settings__.getLocalizedString(202))
					return False
				#get the number of episodes.
				epCount = int(details[u'episodes']) if details[u'episodes'] is not None else 0

				if count == epCount and epCount != 0:
					self.output.log(details['title'] + " " + __settings__.getLocalizedString(302), xbmc.LOGNOTICE)
					if a.add({'anime_id':malID, 'status':'completed', 'episodes':count}) == False:
						self.output.notify(__settings__.getLocalizedString(202))
						return False
					showCount = showCount + 1
				elif (count != 0 and (epCount == 0 or epCount > count)):
					self.output.log(details['title'] + " " + __settings__.getLocalizedString(303) + " " + str(count), xbmc.LOGNOTICE)
					if a.add({'anime_id':malID, 'status':'watching', 'episodes':count}) == False:
						self.output.notify(__settings__.getLocalizedString(202))
						return False
					showCount = showCount + 1
				elif count == 0:
					self.output.log(details['title'] + " " + __settings__.getLocalizedString(304), xbmc.LOGNOTICE)
					if a.add({'anime_id':malID, 'status':'plan to watch', 'episodes':count}) == False:
						self.output.notify(__settings__.getLocalizedString(202))
						return False
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
o = xbmal.output()
if (len(sys.argv) > 1):
	callmal = xbmal.MAL(True)
else:
	callmal = xbmal.MAL(False)
a = callmal.a
if (a == -1 or a == False):
	sys.exit(0)
else:
	while not xbmc.abortRequested:
		xbmc.sleep(100)
sys.exit(0)
