#!/usr/bin/env python
import jsonrpclib, sys

if (len(sys.argv) < 5 or len(sys.argv) > 5):
	print "Usage: " + sys.argv[0] + " server port user pass"
else:
	server = jsonrpclib.Server("http://" + sys.argv[3] + ":" + sys.argv[4] + "@" + sys.argv[1] + ":" + sys.argv[2] + "/jsonrpc")
	results = server.VideoLibrary.GetEpisodes(properties=["tvshowid","season","showtitle","playcount"],sort={"method":"episode"})
	print str(results)
	print
	print "Copy and paste the above to xbmclogs.com for debugging purposes."
