#!/usr/bin/env python
import xbmc, xbmcaddon, xbmcgui, simplejson, os, sys, itertools
from operator import itemgetter
__settings__ 	= xbmcaddon.Addon(id='script.xbmal')
__cwd__		= __settings__.getAddonInfo('path')
__icon__	= os.path.join(__.cwd__, "icon.png")
__scriptname__	= "XBMAL"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join(__cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import myanimelist

class MAL():
	def __init__(self):
		pass

	def malLogin(self):
		mal = myanimelist.MAL((str(__settings__.getSetting("malUser")), str(__settings__.getSetting("malPass")), "mal-api.com", "Basic Agent"))
		if (mal.verify_user() == False):
			xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,__settings__.getLocalizedString(200),10,__icon__))
			xbmc.log("### [%s] - $s" % (__scriptname__,__settings__.getLocalizedString(200)), level=xbmc.LOGDEBUG)
			return None
		else:
			mal.init_anime()
			return mal.anime

'''	def generateMenu(self, message, prompt, items):
		print message
		count = 0
		for item in items:
			print str(count) + ") " + item['title']
			count = count + 1
		selected = raw_input(prompt + " >") #Need error checking at some point...
		print "\n\n"		
		return items[int(selected)]['id']

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

	def getConfiguredXBMCids(self, parsedConfig):
		results = []
		for item in parsedConfig:
			results.append({'xbmc':item['xbmc'], 'season':item['season']})
		return results

	def manualSearch(self, show, season):
		term = raw_input("MAL Search for " + show + " season " + str(season) + "> ")
		results = []
		for item in a.search(term.encode('ascii', 'ignore')).values():
			results.append({'title':item['title'].encode('ascii', 'ignore'), 'id':item['id']})
		results.append({'title':'None of the above', 'id':"%skip%"})
		results.append({'title':'Search Again', 'id':'###'})
		print "\n"
		result = generateMenu("Select a result.", "Your Selection", results)
		if (result == "###"):
			result = manualSearch(show, season)
		return result

	def autoSearch(self, show, season):
		results = []
		for item in a.search(show).values():
			results.append({'title':item['title'].encode('ascii', 'ignore'), 'id':item['id']})
		results.append({'title':"None of the above", 'id':"%skip%"})
		results.append({'title':"Manual Search", 'id':"###"})
		result = generateMenu("Which show is " + show + " Season " + str(season) + "?", "Your Selection", results)
		if (result == "###"):
			result = manualSearch(show, season)
		return result	

	def modifyConfig(self, filename):
		completed = parseConfig(filename)
		menu=[]
		for item in completed:
			menu.append({'title':xbmc.VideoLibrary.GetTVShowDetails(int(item['xbmc']))[u'tvshowdetails'][u'label'].encode('ascii', 'ignore') + " Season " + item['season'], 'id':item['xbmc'] + "," + item['season']})
		menu.append({'title':'Exit', 'id':'X'})
		while 1:
			edit = generateMenu("Which show should we modify?", "Your Selection", menu)
			if edit == 'X':
				 break
			eid, eseason = edit.split(',')
			update = autoSearch(xbmc.VideoLibrary.GetTVShowDetails(int(eid))[u'tvshowdetails'][u'label'].encode('ascii', 'ignore'), eseason)
			for num,item in enumerate(completed):
				if item['xbmc'] == eid and item['season'] == eseason:
					item['mal'] = update
					completed[num] = item
		f = open(filename, 'w')
		for item in completed:
			f.write(str(item['xbmc']) + " | " + str(item['season']) + " | " + str(item['mal']) + "\n")
		f.close()

	def generateConfig(self, filename):
		completed = parseConfig(filename)
		completeShows = getConfiguredXBMCids(completed)
		f = open(filename, 'a')
		tvshows = xbmc.VideoLibrary.GetTVShows()[u'tvshows']
		for tvshow in tvshows:
			seasons = xbmc.VideoLibrary.GetSeasons(tvshow[u'tvshowid'])[u'limits'][u'total']
			for season in range(1, seasons+1):
				if ({'xbmc':str(tvshow[u'tvshowid']), 'season':str(season)} not in completeShows):
					episodes = xbmc.VideoLibrary.GetEpisodes(tvshow[u'tvshowid'], season)
					exists = False
					if u'episodes' in episodes:
						exists = True
						show = autoSearch(tvshow[u'label'].encode('ascii', 'ignore'), season)
					if exists is True:
						f.write(str(tvshow[u'tvshowid']) + " | " + str(season) + " | " + str(show) + "\n")
		f.close()'''
		

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
				else:
					a.update(mal, {'status':'completed', 'episodes':watchedEpisodes, 'score':score})
			elif (watchedEpisodes != 0):
				if epCount == 0 or epCount > watchedEpisodes:
					if watchStatus is None:
						a.add({'anime_id':mal, 'status':'watching', 'episodes':watchedEpisodes})
					else:
						a.update(mal, {'status':'watching', 'episodes':watchedEpisodes, 'score':score})
			elif (watchedEpisodes == 0):
				if watchStatus is None:
					a.add({'anime_id':mal, 'status':'plan to watch', 'episodes':watchedEpisodes})
			#all other scenarios skipped, as they are inconsisancies. Also, I can't spell.
				

	def fullUpdate(self, filename):
		completed = parseConfig(filename)
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
					updateMal(int(season[0]['tvshowid']), int(season[0]['season']), int(malID), count)	
				

class XBMCPlayer( xbmc.Player ):
	def __init__(self, *args):
		pass

	def onPlayBackEnded( self ):
		mal = MAL()
		mal.fullUpdate(xbmc.translatePath( os.path.join( __cwd__, "resources", "config") )

	def onPlayBackStopped( self ):
		mal = MAL()
		mal.fullUpdate(xbmc.translatePath( os.path.join( __cwd__, "resources", "config") )

class XBMCMonitor( xbmc.Monitor ):
	def __init__(self, *args):
		pass

	onDatabaseUpdated(self, database):
		mal = MAL()
		mal.fullUpdate(xbmc.translatePath( os.path.join( __cwd__, "resources", "config") )

#Entry point
player = XBMCPlayer()
monitor = XBMCMonitor()
a = mal.malLogin()
if (a != None):
	while not xbmc.abortRequested: #Main loop
		xbmc.sleep(100)
