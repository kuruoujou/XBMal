#!/usr/bin/env python
import xbmc, os, sys, inspect
#Love stackoverflow. From Sorin Sbarnea, in question 279237
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)
from lib import myanimelist

## Read the user file, get passwords and things.
#Need to re-write to grab from XBMC interface
"""
xuser = ""
xpassword = ""
xserver = "localhost"
xport = "8080"
muser = ""
mpassword = ""
try:
	f = open("users", 'r')
except IOError as e:
	print "Error! users file does not exist. Check the README for info."
	quit()
section = 0
for line in f.readlines():
	line = line.strip()
	if line == "" or line[0] == "#":
		continue #skip comments and blank lines
	elif line == "[xbmc]":
		section = 1
	elif line == "[mal]":
		section = 2
	else:
		if section == 0:
			print "Users file invalid. Check the file format and try again."
			quit()
		items = line.split("=")
		if section == 1:
			if (items[0] == "username"):
				xuser = items[1]
			elif (items[0] == "password"):
				xpassword = items[1]
			elif (items[0] == "server"):
				xserver = items[1]
			elif (items[0] == "port"):
				xport = items[1]
		elif section == 2:
			if (items[0] == "username"):
				muser = items[1]
			elif (items[0] == "password"):
				mpassword = items[1]
if (xuser == "" or xpassword == ""):
	xbmc = jsonrpclib.Server('http://' + xserver + ':' + xport + "/jsonrpc")
else:
	xbmc = jsonrpclib.Server('http://' + xuser + ":" + xpassword + "@" + xserver + ":" + xport + "/jsonrpc")
"""
mal = myanimelist.MAL((muser, mpassword, "mal-api.com", "Basic Agent"))
if (mal.verify_user() == False):
	print "Error! MAL user could not be verified. Exiting..."
	quit()
mal.init_anime()
a = mal.anime


def generateMenu(message, prompt, items):
	print message
	count = 0
	for item in items:
		print str(count) + ") " + item['title']
		count = count + 1
	selected = raw_input(prompt + " >") #Need error checking at some point...
	print "\n\n"		
	return items[int(selected)]['id']

def parseConfig(filename):
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

def getConfiguredXBMCids(parsedConfig):
	results = []
	for item in parsedConfig:
		results.append({'xbmc':item['xbmc'], 'season':item['season']})
	return results

def manualSearch(show, season):
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

def autoSearch(show, season):
	results = []
	for item in a.search(show).values():
		results.append({'title':item['title'].encode('ascii', 'ignore'), 'id':item['id']})
	results.append({'title':"None of the above", 'id':"%skip%"})
	results.append({'title':"Manual Search", 'id':"###"})
	result = generateMenu("Which show is " + show + " Season " + str(season) + "?", "Your Selection", results)
	if (result == "###"):
		result = manualSearch(show, season)
	return result	

def modifyConfig(filename):
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

def generateConfig(filename):
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
	f.close()
	

def updateMal(xbmc, season, mal, watchedEpisodes):
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
				#print "add: completed", 
				a.add({'anime_id':mal, 'status':'completed', 'episodes':watchedEpisodes})
			else:
				#print "update: completed, " + str(score),
				a.update(mal, {'status':'completed', 'episodes':watchedEpisodes, 'score':score})
		elif (watchedEpisodes != 0):
			if epCount == 0 or epCount > watchedEpisodes:
				if watchStatus is None:
					#print "add: watching, " + str(watchedEpisodes) + " episodes",
					a.add({'anime_id':mal, 'status':'watching', 'episodes':watchedEpisodes})
				else:
					#print "update: watching, " + str(watchedEpisodes) + " episodes, " + str(score),
					a.update(mal, {'status':'watching', 'episodes':watchedEpisodes, 'score':score})
		elif (watchedEpisodes == 0):
			if watchStatus is None:
				#print "add: plan to watch", 
				a.add({'anime_id':mal, 'status':'plan to watch', 'episodes':watchedEpisodes})
		#all other scenarios skipped, as they are inconsisancies. Also, I can't spell.
			

def fullUpdate(filename):
	completed = parseConfig(filename)
	tvshows = xbmc.VideoLibrary.GetTVShows()[u'tvshows']
	for tvshow in tvshows:
		seasons = xbmc.VideoLibrary.GetSeasons(tvshow[u'tvshowid'])[u'limits'][u'total']
		for season in range(1, seasons+1):
			malID = -1
			for item in completed:
				if int(tvshow[u'tvshowid']) == int(item['xbmc']) and int(season) == int(item['season']):
					malID = item['mal']
					break
			if (malID == -1 or malID == '%skip%'):
				break #Move to next season
			episodes = xbmc.VideoLibrary.GetEpisodes(tvshow[u'tvshowid'], season, ["playcount", "episode"])
			if u'episodes' in episodes:
				episodes = episodes[u'episodes']
				count = 0
				for episode in episodes:
					if (episode[u'playcount'] != 0 and episode[u'label'][0] != 'S'):
						count = count + 1
				updateMal(int(tvshow[u'tvshowid']), int(season), int(malID), count)
				print tvshow[u'label'] + " season " + str(season) + " updated."
					

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1] == "-c": #Generate default config
		generateConfig("config")
	elif len(sys.argv) == 3 and sys.argv[1] == "-c": #Generate custom config
		generateConfig(sys.argv[2])
	elif len(sys.argv) == 2 and sys.argv[1] == "-m": #modify default config
		modifyConfig("config")
	elif len(sys.argv) == 3 and sys.argv[1] == "-m": #modify custom config
		modifyConfig(sys.argv[2])
	elif len(sys.argv) == 2 and sys.argv[1] != "-c" and sys.argv[1] != "-m": #Run with custom config
		fullUpdate(sys.argv[1])
	elif len(sys.argv) > 2 and sys.argv[1] != "-c": #Unknown
		print "Usage: " + sys.argv[0] + " [-c] [filename] [-m] [filename]"
	elif len(sys.argv) == 1: #Run with default config
		fullUpdate("config")
