# =============================================================================
# lib/myanimelist.py
# This module is made for the Unofficial MAL API: http://mal-api.com/
#
# Copyright (c) 2009 Frank Smit (FSX)
# License: GPL v3, see the COPYING file for details
#
# Modified 5/21/2012 by Spencer Julian
# =============================================================================
  
import os
import re
import sys
import urllib
  
try:
    import json
except ImportError:
    import simplejson as json
  
import utils
import request
  
class MAL():
  
    def __init__(self, config):
  
        self.username, self.password, self.host, self.user_agent = config
        self.request = request.Request(config)
  
        self.anime = None
        self.manga = None
  
    def init_anime(self):
        self.anime = Anime(self.username, self.request)
  
    def init_manga(self):
        pass
  
    def verify_user(self):
        """Verify user details."""
  
        try:
            self.request.execute(path='account/verify_credentials', authenticate=True)
        except (request.HttpRequestError, request.HttpStatusError):
            print str(request.HttpRequestError)
            print str(request.HttpStatusError)
            return False
        else:
            return True
  
class Anime():
  
    def __init__(self, username, request):
  
        self.username = username
        self.request = request

    def getEpisodes(self, episodes):
        if episodes != None:
            return episodes
        else:
            return 0
  
    def list(self):
        """Fetch/Download anime list from MAL."""
  
        try:
            response = self.request.execute(path='animelist/%s' % urllib.quote(self.username), authenticate=True)
        except (request.HttpRequestError, request.HttpStatusError):
            return False
  
        # All the data goes into a new dict
        response_data = json.loads(response)['anime']
        data = {}
  
        for e in response_data:
                data[int(e['id'])] = {
                    'id':               int(e['id']),
                    'title':            utils.htmldecode(e['title']),
                    'type':             e['type'],             # TV, Movie, OVA, ONA, Special, Music
                    'episodes':         self.getEpisodes(e['episodes']),
                    'status':           e['status'],           # finished airing, currently airing, not yet aired
                    'watched_status':   e['watched_status'],   # watching, completed, on-hold, dropped, plan to watch
                    'watched_episodes': int(e['watched_episodes']),
                    'score':            int(e['score']),
                    'image':            e['image_url']
                    }
  
        response_data = None
  
        return data
  
    def search(self, query):
        """Fetch/Download anime list from MAL."""
  
        try:
            response = self.request.execute(path='anime/search?q=%s' % urllib.quote(query))
        except (request.HttpRequestError, request.HttpStatusError):
            return False
  
        # All the data goes into a new dict to keep because the API
        # doesn't provide all the information yet.
        response_data = json.loads(response)
        data = {}
  
        for e in response_data:
                data[int(e['id'])] = {
                    'id':               int(e['id']),
                    'title':            utils.htmldecode(e['title']),
                    'type':             e['type'],             # TV, Movie, OVA, ONA, Special, Music
                    'episodes':         self.getEpisodes(e['episodes']),
                    #'status':           e['status'],           # finished airing, currently airing, not yet aired
                    'members_score':    float(e['members_score']),
                    'image':            e['image_url']
                    }
  
        return data
  
    def add(self, params):
        """Add anime to list.  params = (id, status, episodes, score)."""
  
        try:
            response = self.request.execute(path='animelist/anime', params=params, method='POST', authenticate=True)
        except (request.HttpRequestError, request.HttpStatusError):
            return False
        else:
            return response
  
    def update(self, id, params):
        """Update anime in the list.  data = {status, episodes, score}."""
  
        try:
            params['_method'] = 'put'
            response = self.request.execute(path='animelist/anime/%s' % id, params=params, method='POST', authenticate=True)
        except (request.HttpRequestError, request.HttpStatusError):
            return False
        else:
            return response
  
    def delete(self, id):
        """Remove anime from the list."""
  
        try:
            response = self.request.execute(path='animelist/anime/%s' % id, method='DELETE', authenticate=True)
        except (request.HttpRequestError, request.HttpStatusError):
            return False
        else:
            # Note: Do 'return response' to return the details of the removed anime.
            # The returned details could be used to make an undo function.
            return True
  
    def details(self, id, mine=0):
        """Get information about an anime."""
  
        try:
            response = self.request.execute(path='anime/%s?mine=%d' % (id, mine), authenticate=True)
        except (request.HttpRequestError, request.HttpStatusError):
            return False
        else:
            return json.loads(response)
  
    def image(self, url):
        """Get the image of the anime."""
  
        filename, headers = self.request.retrieve(url)
  
        # Check mimetype of image (only Jpeg at the moment)
        if re.match('.*(Content-Type: image/jpeg).*', str(headers), re.DOTALL) is None:
            return False
  
        return filename
  
