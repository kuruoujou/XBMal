#!/usr/bin/env python
import xbmc, xbmcaddon, xbmcgui, simplejson, os, sys, itertools
from operator import itemgetter
__settings__ 	= xbmcaddon.Addon(id='script.xbmal')
__cwd__		= __settings__.getAddonInfo('path')
__icon__	= os.path.join(__cwd__, "icon.png")
__scriptname__	= "XBMAL"

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

	def updateMal(self, xbmc, season, mal, watchedEpisodes):
		details = a.details(mal, 1)
		watchStatus = details[u'watched_status']
		if details[u'episodes'] is not None:
			epCount = int(details[u'episodes'])
		else:
			epCount = 0
		if details[u'watched_episodes'] is not None:
			epWatchedMal = int(details[u'watched_episodes'])
		else:
			epWatchedMal = 0
		if details[u'score'] is not None:
			score = int(details[u'score'])
		else:
			score = 0
		if watchStatus == u'watching' or watchStatus == u'plan to watch' or watchStatus == None: #Only want to mess with currently watching shows or shows planned to be watched, or shows not on the list at all, for now.
			if epCount == watchedEpisodes and epCount != 0:
				if watchStatus is None:
					a.add({'anime_id':mal, 'status':'completed', 'episodes':watchedEpisodes})
					return True;
				else:
					a.update(mal, {'status':'completed', 'episodes':watchedEpisodes, 'score':score})
					return True;
			elif (watchedEpisodes != 0):
				if epCount == 0 or epCount > watchedEpisodes:
					if watchStatus is None:
						a.add({'anime_id':mal, 'status':'watching', 'episodes':watchedEpisodes})
						return True;
					else:
						a.update(mal, {'status':'watching', 'episodes':watchedEpisodes, 'score':score})
						return True;
			elif (watchedEpisodes == 0):
				if watchStatus is None:
					a.add({'anime_id':mal, 'status':'plan to watch', 'episodes':watchedEpisodes})
					return True;
			#all other scenarios skipped, as they are inconsisancies. Also, I can't spell.
		return False;
				

	def fullUpdate(self, filename):
		xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,__settings__.getLocalizedString(300),10,__icon__))
		showCount = 0;
		completed = self.parseConfig(filename)
		#Most of this is from the watchlist code, because we're doing something very similar.
		json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes","params":{"properties":["tvshowid","playcount","season"], "sort": {"method":"episode"} }, "id":1}')
		json_query = unicode(json_query, 'utf-8', errors='ignore')
		json_response = simplejson.loads(json_query)
		if json_response['result'].has_key('episodes'):
			json_response = json_response['result']['episodes']
			#the list is sorted by episode number, then tvshow id. Want a seperate list for each tv show.
			tvshows = [list(group) for key,group in itertools.groupby(sorted(json_response, key=itemgetter('tvshowid')), key=itemgetter('tvshowid'))]
			for tvshow in tvshows:
				seasons = [list(group) for key,group in itertools.groupby(sorted(tvshow, key=itemgetter('season')), key=itemgetter('season'))]
				for season in seasons:
					if season[0]['season'] == 0:
						continue #Don't do "season 0"
					malID = -1
					for item in completed:
						if int(season[0]['tvshowid']) == int(item['xbmc']) and int(season[0]['season']) == int(item['season']):
							malID = item['mal']
					if (malID == -1 or malID == '%skip%'):
						continue #move on...
					count = 0
					for episode in season:
						if(episode['playcount'] != 0 and episode['label'][0] != 'S'):
							count = count + 1
					if self.updateMal(int(season[0]['tvshowid']), int(season[0]['season']), int(malID), count):
						showCount = showCount + 1
		xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,str(showCount) + " " + __settings__.getLocalizedString(301),10,__icon__))
				

class XBMCPlayer( xbmc.Player ):
	def __init__(self, *args):
		xbmc.Player.__init__(self)

	def onPlayBackEnded( self ):
		mal = MAL()
		mal.fullUpdate(xbmc.translatePath( os.path.join( __cwd__, "resources", "config") ))

	def onPlayBackStopped( self ):
		mal = MAL()
		mal.fullUpdate(xbmc.translatePath( os.path.join( __cwd__, "resources", "config") ))

#class XBMCMonitor( xbmc.Monitor ):
#	def __init__(self, *args):
#		pass

#	def onDatabaseUpdated(self, database):
#		xbmc.log("### [%s] - %s" %(__scriptname__,"Database Updated, Updating..."), level=xbmc.LOGNOTICE)
#		mal = MAL()
#		mal.fullUpdate(xbmc.translatePath( os.path.join( __cwd__, "resources", "config") ))

#Entry point
player = XBMCPlayer()
#monitor = XBMCMonitor()
mal = MAL()
a = mal.malLogin()
if (a != None):
	while not xbmc.abortRequested: #Main loop
		xbmc.sleep(100)
