#!/usr/bin/env python

import xbmc, xbmcgui, xbmcaddon, simplejson, os, sys, itertools, math
from operator import itemgetter

__settings__    = xbmcaddon.Addon(id='script.xbmal')
__cwd__         = __settings__.getAddonInfo('path')
__icon__        = os.path.join(__cwd__, "icon.png")
__scriptname__  = "XBMAL Setup"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join(__cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import myanimelist

class ListGenerator():
	def __init__(self):
		self.a = self.malLogin()

	def malLogin(self):
                mal = myanimelist.MAL((str(__settings__.getSetting("malUser")), str(__settings__.getSetting("malPass")), "mal-api.com", "Basic Agent"))
                if (mal.verify_user() == False):
                        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,__settings__.getLocalizedString(200),10,__icon__))
                        xbmc.log("### [%s] - %s" % (__scriptname__,__settings__.getLocalizedString(200)), level=xbmc.LOGFATAL)
                        return None
                else:   
                        mal.init_anime()
                        return mal.anime
	
	def generateList(self, ret):
		returnList = []
		json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes","params":{"properties":["tvshowid","season","showtitle"], "sort": {"method":"episode"} }, "id":1}') 
                json_query = unicode(json_query, 'utf-8', errors='ignore') 
                json_response = simplejson.loads(json_query) 
                if json_response['result'].has_key('episodes'): 
                        json_response = json_response['result']['episodes'] 
                        #the list is sorted by episode number, then tvshow id. Want a seperate list for each tv show. 
                        tvshows = [list(group) for key,group in itertools.groupby(sorted(json_response,key=itemgetter('tvshowid')),key=itemgetter('tvshowid'))]
			totalShows = len(tvshows)
			currentShow = 0
                        for tvshow in tvshows: 
				currentShow = currentShow + 1
				ret.update(int(((float(currentShow)/float(totalShows))*100)))
                                seasons = [list(group) for key,group in itertools.groupby(sorted(tvshow, key=itemgetter('season')), key=itemgetter('season'))] 
                                for season in seasons: 
					if(ret.iscanceled()): 
						return False
                                        if season[0]['season'] == 0: 
                                                continue #Don't do "season 0"
					searchResults = self.a.search(season[0]['showtitle'].encode('ascii', 'ignore'))
					if (searchResults is False):
						searchResult = {'id':'%skip%', 'title':__settings__.getLocalizedString(411)}
					else:
						searchResult = self.a.search(season[0]['showtitle'].encode('ascii','ignore')).values()
					if len(searchResult) != 0:
						searchResult = searchResult[0]
					else:
						searchResult = {'id':'%skip%', 'title':__settings__.getLocalizedString(400)}
					returnList.append({'xbmcID':str(season[0]['tvshowid']), 'xbmcTitle':season[0]['showtitle'], 'xbmcSeason':str(season[0]['season']), 'malID':str(searchResult['id']), 'malTitle':searchResult['title']})
		returnList.append({'xbmcID':'-1', 'xbmcTitle':__settings__.getLocalizedString(401), 'xbmcSeason':'0', 'malID':'%done%', 'malTitle':''})
		return returnList

	def generateFix(self, item):
		returnList = []
		for result in self.a.search(item['xbmcTitle'].encode('ascii','ignore')).values():
			returnList.append({'xbmcID':item['xbmcID'], 'xbmcTitle':item['xbmcTitle'], 'xbmcSeason':item['xbmcSeason'], 'malID':result['id'], 'malTitle':result['title']})
		returnList.append({'xbmcID':item['xbmcID'], 'xbmcTitle':item['xbmcTitle'], 'xbmcSeason':item['xbmcSeason'], 'malID':'%skip%', 'malTitle':__settings__.getLocalizedString(402)})
		returnList.append({'xbmcID':'-1', 'xbmcTitle':__settings__.getLocalizedString(403), 'xbmcSeason':'0', 'malID':'%manual%', 'malTitle':''})
		return returnList

	def generateSelection(self, mappings, fullList=True):
		displayStrings = []
		if fullList == True:
			for item in mappings:
				if (item['xbmcID'] != '-1'):
					displayStrings.append(item['xbmcTitle'] + " S" + item['xbmcSeason'] + " -> " + item['malTitle'])
				else:
					displayStrings.append(item['xbmcTitle'])
		else:
			for item in mappings:
				if (item['xbmcID'] != '-1'):
					displayStrings.append(item['malTitle'])
				else:
					displayStrings.append(item['xbmcTitle'])
		return displayStrings


class MainDiag():
	def __init__(self):
		pDialog = xbmcgui.DialogProgress()
		pDialog.create(__settings__.getLocalizedString(408))
		pDialog.update(0, __settings__.getLocalizedString(410))
		lg = ListGenerator()
		if (lg.a != False):
			pDialog.update(0, __settings__.getLocalizedString(404), __settings__.getLocalizedString(405))
			mappings = lg.generateList(pDialog)
			pDialog.close()
			if mappings != False:
				selectedItem = 0
				doWrite = True
				while selectedItem != len(mappings) - 1:
					ListDialog = xbmcgui.Dialog()
					selectedItem = ListDialog.select(__settings__.getLocalizedString(409), lg.generateSelection(mappings))
					if (selectedItem != len(mappings) - 1 and selectedItem != -1):
						possibleReplacements = lg.generateFix(mappings[selectedItem])
						newResult = ListDialog.select(__settings__.getLocalizedString(406) + " " + mappings[selectedItem]['xbmcTitle'], lg.generateSelection(possibleReplacements, False))
						if (newResult != len(possibleReplacements) - 1 and newResult != -1):
							mappings[selectedItem] = possibleReplacements[newResult]
						elif (newResult != -1):
							pass #Need to make a manual search here
					if(selectedItem == -1):
						doWrite = False
						break
				#Need to call a re-write function here.
		else:
			pDialog.close()
				

w = MainDiag()
