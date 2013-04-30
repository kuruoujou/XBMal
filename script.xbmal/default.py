#!/usr/bin/env python
import xbmc, xbmcgui, xbmcaddon, simplejson, os, sys, itertools, math
import xml.etree.ElementTree as et
from operator import itemgetter

__settings__    = xbmcaddon.Addon(id='script.xbmal')
__cwd__         = __settings__.getAddonInfo('path')
__icon__        = os.path.join(__cwd__, "icon.png")
__configFile__  = xbmc.translatePath('special://profile/addon_data/script.xbmal/config.xml')
__scriptname__  = "XBMAL Setup"
__updaterFile__	= xbmc.translatePath( os.path.join(__cwd__, 'updater.py') )

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join(__cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import myanimelist, xbmal

class ListGenerator():
	def __init__(self):
		self.config = xbmal.XML()
		self.mal = xbmal.MAL()
		self.server = xbmal.server()
		self.output = xbmal.output()
		self.a = self.mal.a

	def generateList(self, ret):
		""" Generates a list of elements to be mapped """
		returnList = self.config.parseConfig() #returns a list of elements
		tvshows = self.server.getXBMCshows()
		totalShows = len(tvshows)
		currentShow = 0
		for tvshow in tvshows: 
			currentShow = currentShow + 1
			ret.update(int(((float(currentShow)/float(totalShows))*100)))
			seasons = self.server.getXBMCseasons(tvshow)
			for season in seasons: 
				if(ret.iscanceled()):
					return False
				if season[0]['season'] == 0: 
					continue #Don't do "season 0"
				if self.config.showInConfig(season[0]['tvshowid'], season[0]['season']) == False:
					try:
						self.output.log("Listing Show: " + season[0]['showtitle'].__repr__().encode('ascii', 'ignore'), xbmc.LOGNOTICE)
					except:
						self.output.log("The problematic show appears to be the next one, alphebetically. Please send this log along with the name of that show to the developer via github and xbmclogs.com.", xbmc.LOGNOTICE)
					searchResults = self.a.search(season[0]['showtitle'].__repr__().encode('ascii', 'ignore'))
					if (searchResults is False):
						searchResult = [{'id':'%skip%', 'title':__settings__.getLocalizedString(411)}]
					else:
						searchResult = searchResults.values()
					if len(searchResult) != 0:
						searchResult = searchResult[len(searchResult)-1] #The last item is usually the closest.
					else:
						searchResult = {'id':'%skip%', 'title':__settings__.getLocalizedString(400)}
					returnList = self.config.add(str(season[0]['tvshowid']), str(season[0]['season']), season[0]['showtitle'], str(searchResult['id']), searchResult['title'])
		return returnList

	def generateFix(self, item, searchString=False):
		""" generates a list of results to fix a single mapping """
		returnList = []
		if searchString == False or searchString == "":
			searchString = item.get('xbmcTitle')
		for result in self.a.search(searchString.encode('ascii','ignore')).values():
			returnList.append(et.Element('show', attrib={'xbmcID':item.get('xbmcID'), 'season':item.get('season'), 'xbmcTitle':item.get('xbmcTitle'), 'malID':str(result['id']), 'malTitle':result['title']}))
		returnList.append(et.Element('show', attrib={'xbmcID':item.get('xbmcID'), 'xbmcTitle':item.get('xbmcTitle'), 'season':item.get('season'), 'malID':'%skip%', 'malTitle':__settings__.getLocalizedString(402)}))
		return returnList

	def generateSelection(self, mappings, fullList=True):
		""" Takes a list of elements and generates a readable list in the same order. """
		displayStrings = []
		if fullList == True:
			for item in mappings:
				displayStrings.append(item.get('xbmcTitle') + " S" + str(item.get('season')) + " -> " + item.get('malTitle'))
			displayStrings.append(__settings__.getLocalizedString(401))
		else:
			for item in mappings:
				displayStrings.append(item.get('malTitle'))
			displayStrings.append(__settings__.getLocalizedString(403))
		return displayStrings


class MainDiag():
	def __init__(self):
		#Generate a progress dialog
		pDialog = xbmcgui.DialogProgress()
		pDialog.create(__settings__.getLocalizedString(408))
		pDialog.update(0, __settings__.getLocalizedString(410))
		#Create the listgenerator
		lg = ListGenerator()
		if (lg.a != False and lg.a != -1): #If lg.a is False, then we can't login to MAL. Exit.
			pDialog.update(0, __settings__.getLocalizedString(404), __settings__.getLocalizedString(405))
			#Generate the XBMC to MAL list
			mappings = lg.generateList(pDialog)
			pDialog.close()
			#if mappings is false, then something went wrong in generateList. Exit.
			if mappings != False:
				selectedItem = 0
				doWrite = True
				#We're looping until the final selection is made - either "back" or the write command.
				while selectedItem != len(mappings):
					#Create a new Dialog. Did not want to deal with creating a full window, although a virtual file list might be nice...
					ListDialog = xbmcgui.Dialog()
					#Make it a select dialog, and generate a list of strings we can use from the list we got earlier
					selectedItem = ListDialog.select(__settings__.getLocalizedString(409), lg.generateSelection(mappings))
					if (selectedItem != len(mappings) and selectedItem != -1): #-1 is back, last item is write
						#Perform the MAL search for the XBMC title, and create a dialog of all the results.
						possibleReplacements = lg.generateFix(mappings[selectedItem])
						newResult = ListDialog.select(__settings__.getLocalizedString(406) + " " + mappings[selectedItem].get('xbmcTitle'), lg.generateSelection(possibleReplacements, False))
						if (newResult != len(possibleReplacements) and newResult != -1): #-1 is back, last item is manual
							mappings = lg.config.replace(mappings[selectedItem],selectedItem,possibleReplacements[newResult])
						elif (newResult != -1):
							while 1:
								#If it's manual, keep looping until they select something or give up (none or back)
								possibleReplacements = lg.generateFix(mappings[selectedItem], self.manualSearch())
								newResult = ListDialog.select(__settings__.getLocalizedString(406) + " " + mappings[selectedItem].get('xbmcTitle'), lg.generateSelection(possibleReplacements, False))
								if (newResult != len(possibleReplacements) and newResult != -1):
									mappings = lg.config.replace(mappings[selectedItem],selectedItem,possibleReplacements[newResult])
									break
								elif (newResult == -1):
										break
					if(selectedItem == -1): #In this case, we backed out of the main select dialog
						doWrite = False
						break
				if doWrite: #Write the config file
					pDialog.create(__settings__.getLocalizedString(413))
					lg.config.writeConfig()
					pDialog.close()
				xbmc.executebuiltin("XBMC.RunScript(" +  __updaterFile__ + ", True)")#If the main script isn't running, run it now.
				lg.output.notify(__settings__.getLocalizedString(414))
		else:
			pDialog.close() #and we're done!


	def manualSearch(self):
		""" Creates a keyboard for a manual search """
		kb = xbmc.Keyboard()
		kb.setHeading(__settings__.getLocalizedString(412))
		kb.doModal()
		if (kb.isConfirmed()):
			return kb.getText()
		else:
			return False
				

w = MainDiag()
