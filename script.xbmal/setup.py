#!/usr/bin/env python

import xbmc, xbmcgui, xbmcaddon, simplejson, os, sys, itertools, math
from operator import itemgetter

__settings__    = xbmcaddon.Addon(id='script.xbmal')
__cwd__         = __settings__.getAddonInfo('path')
__icon__        = os.path.join(__cwd__, "icon.png")
__configFile__ 	= xbmc.translatePath('special://profile/addon_data/script.xbmal/config')
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

	
	def generateList(self, ret):
		configList = self.parseConfig(__configFile__)
		configShows = {}
		for item in configList:
			configShows[item['xbmc'] + '.' + item['season']] = item['mal']
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
					inConfig = False
					if str(season[0]['tvshowid']) + '.' + str(season[0]['season']) in configShows:
						inConfig = True
						if configShows[str(season[0]['tvshowid']) + '.' + str(season[0]['season'])] == '%skip%':
							searchResult = {'id':'%skip%', 'title':__settings__.getLocalizedString(400)}
						else:
							searchResult = self.a.details(int(configShows[str(season[0]['tvshowid']) + '.' + str(season[0]['season'])]), 1)
					if inConfig == False:
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

	def generateFix(self, item, searchString=False):
		returnList = []
		if searchString == False or searchString == "":
			searchString = item['xbmcTitle']
		for result in self.a.search(searchString.encode('ascii','ignore')).values():
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

	def writeConfig(self, mappings, ret):
		totalMappings = len(mappings)
		cfile = open(__configFile__, 'w')
		xbmc.log("### [%s] - %s" % (__scriptname__,__settings__.getLocalizedString(413)), level=xbmc.LOGNOTICE)
		writeCount = 0
		for mapping in mappings:
			writeCount = writeCount + 1
			ret.update(int(float(writeCount)/float(totalMappings)*100))
			if (str(mapping['xbmcID']) != '-1'):
				cfile.write(str(mapping['xbmcID']) + " | " + str(mapping['xbmcSeason']) + " | " + str(mapping['malID']) + "\n")



class MainDiag():
	def __init__(self):
		#Generate a progress dialog
		pDialog = xbmcgui.DialogProgress()
		pDialog.create(__settings__.getLocalizedString(408))
		pDialog.update(0, __settings__.getLocalizedString(410))
		#Create the listgenerator
		lg = ListGenerator()
		if (lg.a != False): #If lg.a is False, then we can't login to MAL. Exit.
			pDialog.update(0, __settings__.getLocalizedString(404), __settings__.getLocalizedString(405))
			#Generate the XBMC to MAL list
			mappings = lg.generateList(pDialog)
			pDialog.close()
			#if mappings is false, then something went wrong in generateList. Exit.
			if mappings != False:
				selectedItem = 0
				doWrite = True
				#We're looping until the final selection is made - either "back" or the write command.
				while selectedItem != len(mappings) - 1:
					#Create a new Dialog. Did not want to deal with creating a full window, although a virtual file list might be nice...
					ListDialog = xbmcgui.Dialog()
					#Make it a select dialog, and generate a list of strings we can use from the list we got earlier
					selectedItem = ListDialog.select(__settings__.getLocalizedString(409), lg.generateSelection(mappings))
					if (selectedItem != len(mappings) - 1 and selectedItem != -1): #-1 is back, last item is write
						#Perform the MAL search for the XBMC title, and create a dialog of all the results.
						possibleReplacements = lg.generateFix(mappings[selectedItem])
						newResult = ListDialog.select(__settings__.getLocalizedString(406) + " " + mappings[selectedItem]['xbmcTitle'], lg.generateSelection(possibleReplacements, False))
						if (newResult != len(possibleReplacements) - 1 and newResult != -1): #-1 is back, last item is manual
							mappings[selectedItem] = possibleReplacements[newResult]
						elif (newResult != -1):
							while 1:
								#If it's manual, keep looping until they select something or give up (none or back)
								possibleReplacements = lg.generateFix(mappings[selectedItem], self.manualSearch())
								newResult = ListDialog.select(__settings__.getLocalizedString(406) + " " + mappings[selectedItem]['xbmcTitle'], lg.generateSelection(possibleReplacements, False))
								if (newResult != len(possibleReplacements) - 1 and newResult != -1):
									mappings[selectedItem] = possibleReplacements[newResult]
									break
								elif (newResult == -1):
										break
					if(selectedItem == -1): #In this case, we backed out of the main select dialog
						doWrite = False
						break
				if doWrite: #Write the config file
					pDialog.create(__settings__.getLocalizedString(413))
					lg.writeConfig(mappings, pDialog)
					pDialog.close()
		else:
			pDialog.close() #and we're done!


	def manualSearch(self):
		kb = xbmc.Keyboard()
		kb.setHeading(__settings__.getLocalizedString(412))
		kb.doModal()
		if (kb.isConfirmed()):
			return kb.getText()
		else:
			return False
				

w = MainDiag()
