#!/usr/bin/env python
import xbmc, xbmcaddon, xbmcgui, simplejson, os, sys, itertools
from operator import itemgetter
__settings__ 	= xbmcaddon.Addon(id='script.xbmal')
__cwd__		= __settings__.getAddonInfo('path')
__icon__	= os.path.join(__cwd__, "icon.png")
__scriptname__	= "XBMAL"
__configFile__	= xbmc.translatePath('special://profile/addon_data/script.xbmal/config')

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join(__cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import myanimelist

class MAL():
	def __init__(self):
		pass

	def parseConfig(self, filename):
		try:
			f = open(filename, 'r')
		except IOError as e:
			return []
		results = []
		for line in f.readlines():
			shows = line.split(' | ')
			results.append({'xbmc':shows[0].strip(), 'season':shows[1].strip(), 'mal':shows[2].strip()})
		f.close()
		return results

	def malLogin(self):
		mal = myanimelist.MAL((str(__settings__.getSetting("malUser")), str(__settings__.getSetting("malPass")), "mal-api.com", "Basic Agent"))
		if (mal.verify_user() == False):
			xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,__settings__.getLocalizedString(200),10,__icon__))
			xbmc.log("### [%s] - %s" % (__scriptname__,__settings__.getLocalizedString(200)), level=xbmc.LOGFATAL)
			return None
		else:
			mal.init_anime()
			return mal.anime

	def fullUpdate(self, filename):
		xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,__settings__.getLocalizedString(300),20,__icon__))
		showCount = 0;
		completed = self.parseConfig(filename)
		allShows = {}
		for item in completed:
			allShows[item['xbmc'] + "." + item['season']] = item['mal']
		#Get current MAL list (dictionary of dictionaries)
		malList = a.list()
		malListIDs = malList.keys()
		#Most of this is from the watchlist code, because we're doing something very similar.
		json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes","params":{"properties":["tvshowid","playcount","season"], "sort": {"method":"episode"} }, "id":1}')
		json_query = unicode(json_query, 'utf-8', errors='ignore')
		json_response = simplejson.loads(json_query)
		if json_response['result'].has_key('episodes'):
			json_response = json_response['result']['episodes']
			#the list is sorted by episode number, then tvshow id. Want a seperate list for each tv show.
			tvshows = [list(group) for key,group in itertools.groupby(sorted(json_response,key=itemgetter('tvshowid')),key=itemgetter('tvshowid'))]
			for tvshow in tvshows:
				seasons = [list(group) for key,group in itertools.groupby(sorted(tvshow, key=itemgetter('season')), key=itemgetter('season'))]
				for season in seasons:
					if season[0]['season'] == 0:
						continue #Don't do "season 0"
					malID = -1
					if str(season[0]['tvshowid']) + "." + str(season[0]['season']) in allShows:
						malID = allShows[str(season[0]['tvshowid']) + "." + str(season[0]['season'])]
					#for item in completed:
					#	if int(season[0]['tvshowid']) == int(item['xbmc']) and int(season[0]['season']) == int(item['season']):
					#		malID = item['mal']
					if (malID == -1 or malID == '%skip%'):
						continue #move on...
					malID = int(malID)
					count = 0
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
							epCount = int(details[malID]['episodes'])
						else:
							epCount = 0
					
					if malID in malListIDs:
						if(malList[malID]['watched_status'] == u'watching' or malList[malID]['watched_status'] == u'plan to watch'):
							if count == epCount and epCount != 0:
								xbmc.log("### [%s] - %s" %(__scriptname__,malList[malID]['title'] + " " + __settings__.getLocalizedString(302)), level=xbmc.LOGNOTICE)
								a.update(malID, {'status':'completed', 'episodes':count, 'score':malList[malID]['score']})
								showCount = showCount + 1
							elif (count != 0 and (epCount == 0 or epCount > count)):
								xbmc.log("### [%s] - %s" %(__scriptname__,malList[malID]['title'] + " " + __settings__.getLocalizedString(303) + " " + str(count)), level=xbmc.LOGNOTICE)
								a.update(malID, {'status':'watching', 'episodes':count, 'score':malList[malID]['score']})
								showCount = showCount + 1
					else:
						if count == epCount and epCount != 0:
							xbmc.log("### [%s] - %s" %(__scriptname__,details['title'] + " " + __settings__.getLocalizedString(302)), level=xbmc.LOGNOTICE)
							a.add({'anime_id':malID, 'status':'completed', 'episodes':count})
							showCount = showCount + 1
						elif count != 0 and epCount == 0 or epCount > count:
							xbmc.log("### [%s] - %s" %(__scriptname__,details['title'] + " " + __settings__.getLocalizedString(303) + " " + str(count)), level=xbmc.LOGNOTICE)
							a.add({'anime_id':malID, 'status':'watching', 'episodes':count})
							showCount = showCount + 1
						elif count == 0:
							xbmc.log("### [%s] - %s" %(__scriptname__,details['title'] + " " + __settings__.getLocalizedString(304)), level=xbmc.LOGNOTICE)
							a.add({'anime_id':malID, 'status':'plan to watch', 'episodes':count})
							showCount = showCount + 1
		xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,str(showCount)+" "+__settings__.getLocalizedString(301),20,__icon__))
				

class XBMCPlayer( xbmc.Player ):
	def __init__(self, *args):
		xbmc.Player.__init__(self)
		self.wasVideo = False

	def onPlayBackEnded( self ):
		if self.wasVideo:
			mal = MAL()
			mal.fullUpdate(__configFile__)

	def onPlayBackStopped( self ):
		if self.wasVideo:
			mal = MAL()
			mal.fullUpdate(__configFile__)
	
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
a = mal.malLogin()
while not xbmc.abortRequested:
	if (a != None):
		xbmc.sleep(100)
	else:
		trys = 0
		if (trys <= 5) : #Only want to try 6 times, i.e., for half an hour.
			xbmc.sleep(1000 * 60 * 5) #Wait for 5 minutes before trying again
			a = mal.malLogin()
			trys = trys + 1 
		else:
			break #If it's been half an hour with no updates, break, as the user probably isn't going to update their credentials now.
