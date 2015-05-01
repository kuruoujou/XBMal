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
		tvshows = self.server.getXBMCshows()		
		for tvshow in tvshows:
			seasons = self.server.getXBMCseasons(tvshow)
			prev_malID = 0
			sameTVshow = False
			totalEps = 0
			total_Eps_lastseason = 0
			for season in seasons:
				if season[0]['season'] == 0:
					continue #Don't do "season 0"
				malID = self.config.showInConfig(season[0]['tvshowid'], season[0]['season'])
				if (malID == -1 or malID == '%skip%' or malID == False):
					continue #move on...
				malID = int(malID)
				#checks if the next season is mapped to the same malID as the previous one
				if malID == prev_malID:
					sameTVshow = True
				prev_malID = malID
				count = 0
				#xbmc.log(str(season), xbmc.LOGNOTICE)
				for episode in season:
					totalEps += 1
					if(episode['playcount'] != 0 and episode['label'][0] != 'S'):
						count = count + 1
						#if it's the sameTVshow for MAL add the total episodecount to count
						#this is needed if you added an anime with season numbering (e.g. for scraper convinience) which on MAL doesn't have seasons
						if sameTVshow == True:
							count = count + total_Eps_lastseason
							sameTVshow = False
				if malID in malListIDs:
					if malList[malID]['episodes'] is not None:
						epCount = int(malList[malID]['episodes'])
					else:
						epCount = 0
					if malList[malID]['watched_episodes'] is not None:
						malCount = int(malList[malID]['watched_episodes'])
					else:
						malCount = 0
				else:
					details = a.details(malID)
					if details == False:
						self.output.notify(__settings__.getLocalizedString(202))
						return False
					if details[u'episodes'] is not None:
						epCount = int(details[u'episodes'])
					else:
						epCount = 0
				if malID in malListIDs:
					if(malList[malID]['watched_status'] == u'watching' or malList[malID]['watched_status'] == u'plan to watch'):
						if count == epCount and epCount != 0:
							#XBMC Log can't handle unicode, need workaround
							#self.output.log(malList[malID]['title'].encode('ascii','ignore') + " " + __settings__.getLocalizedString(302), xbmc.LOGNOTICE)
							if a.update(malID, {'status':'completed', 'episodes':count, 'score':malList[malID]['score']}) == False:
								self.output.notify(__settings__.getLocalizedString(202))
								return False
							showCount = showCount + 1
						elif (count != 0 and (epCount == 0 or epCount > count) and malCount < count):
							#self.output.log(malList[malID]['title'].encode('ascii', 'ignore') + " " + __settings__.getLocalizedString(303) + " " + str(count), xbmc.LOGNOTICE)
							if a.update(malID, {'status':'watching', 'episodes':count, 'score':malList[malID]['score']}) == False:
								self.output.notify(__settings__.getLocalizedString(202))
								return False
							showCount = showCount + 1
				else:
					if count == epCount and epCount != 0:
						#self.output.log(details['title'] + " " + __settings__.getLocalizedString(302), xbmc.LOGNOTICE)
						if a.add({'anime_id':malID, 'status':'completed', 'episodes':count}) == False:
							self.output.notify(__settings__.getLocalizedString(202))
							return False
						showCount = showCount + 1
					elif (count != 0 and (epCount == 0 or epCount > count)):
						#self.output.log(details['title'] + " " + __settings__.getLocalizedString(303) + " " + str(count), xbmc.LOGNOTICE)
						if a.add({'anime_id':malID, 'status':'watching', 'episodes':count}) == False:
							self.output.notify(__settings__.getLocalizedString(202))
							return False
						showCount = showCount + 1
					elif count == 0:
						#self.output.log(details['title'] + " " + __settings__.getLocalizedString(304), xbmc.LOGNOTICE)
						if a.add({'anime_id':malID, 'status':'plan to watch', 'episodes':count}) == False:
							self.output.notify(__settings__.getLocalizedString(202))
							return False
						showCount = showCount + 1
				total_Eps_lastseason = totalEps
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
