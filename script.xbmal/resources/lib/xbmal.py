#!/usr/bin/env python

import xbmc, xbmcgui, xbmcaddon, simplejson, os, sys, itertools, math
import xml.etree.ElementTree as et
from operator import itemgetter

__settings__    = xbmcaddon.Addon(id='script.xbmal')
__cwd__         = __settings__.getAddonInfo('path')
__icon__        = os.path.join(__cwd__, "icon.png")
__configFile__  = xbmc.translatePath('special://profile/addon_data/script.xbmal/config.xml')

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join(__cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

import myanimelist

class XML(xmlFile=__configFile__):
	def __init__(self):
		self.xmlFile = xmlFile
		self.tree = et.ElementTree()

	def parseConfig(self):
	""" Parses the configuration XML File, returns a list of XML Elements corresponding to the shows or an empty list"""
		try:
			self.tree.parse(self.xmlFile)
		except IOError:
			self.tree._setroot(et.Element('shows'))
			return []

		return self.tree.findall('show')

	def showInConfig(self, showid, season):
	""" Checks to see if a show is in the config file, based on show id and season, returns the appropriate mal id or false. """
		for item in self.tree.iterfind('show'):
			if (item.attrib['xbmcid'] == str(showid)) and (item.attrib['season'] == str(season)):
				return item.attrib['malid']
		return False

	def replace(self, oldItem, location, item):
	""" Replaces the item with the given id with the given item, returns list of XML Elements """
		self.tree.getroot().remove(oldItem)
		self.tree.getroot().insert(location,item)
		return self.tree.findall('show')

	def add(self, showid, season, title, malid, maltitle):
	""" Adds an item to the config file, returns a list of xml elements """
		et.SubElement(self.tree.getroot(), 'show', attrib={'malID':malid, 'malTitle':maltitle, 'xbmcID':showid, 'season':season, 'xbmcTitle':title})
		return self.tree.findall('show')

	def writeConfig(self):
	""" Writes the configuration xml file."""
		o = output()
		o.log(__settings__.getLocalizedString(413), xbmc.LOGNOTICE)
		self.tree.write(self.xmlFile, encoding="UTF-8", xml_declaration=True)

class MAL():
	def __init__(self):
		self.a = self.malLogin()

	def malLogin(self):
	""" Attempts to log into mal. Returns a mal.anime instance if successful, false if not."""
		mal = myanimelist.MAL((str(__settings__.getSetting("malUser")), str(__settings__.getSetting("malPass")), "mal-api.com", "Basic Agent"))
		if (mal.verify_user() == False):
			o = output()
			o.notify(__settings__.getLocalizedString(200))
			o.log(__settings.getLocalizedString(200),xbmc.LOGFATAL)
			return None
		else:   
			mal.init_anime()
			return mal.anime

class server():
	def __init__(self):
		pass

	def getXBMCshows(self):
	""" Gets all of the TV Shows from the XBMC library. Returns a list of shows if successful, empty list if not."""
		json_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes","params":{"properties":["tvshowid","season","showtitle"], "sort": {"method":"episode"} }, "id":1}')
		json_query = unicode(json_query, 'utf-8', errors='ignore')
		json_response = simplejson.loads(json_query)
		if json_response['result'].has_key('episodes'):
			json_response = json_response['result']['episodes']
			#the list is sorted by episode number, then tvshow id. Want a seperate list for each tv show. 
			tvshows = [list(group) for key,group in itertools.groupby(sorted(json_response,key=itemgetter('tvshowid')),key=itemgetter('tvshowid'))]
		else:
			tvshows = []

		return tvshows

	def getXBMCSeasons(self, tvshow):
	""" Gets all of the seasons for a TV show. Returns a list of episodes if successful, empty list if not."""
		seasons = [list(group) for key,group in itertools.groupby(sorted(tvshow, key=itemgetter('season')), key=itemgetter('season'))]
		return seasons
	

class output():
	def __init__(self):
		pass

	def notify(self, notice):
	""" Sends a notification to XBMC """
		xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,notice,10,__icon__))

	def log(self, msg, loglevel):
	""" Logs into the xbmc.log file """
		xbmc.log("### [%s] - %s" %(__scriptname__,msg), level=loglevel)
