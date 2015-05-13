# =============================================================================
# lib/request.py
#
# Copyright (c) 2009 Frank Smit (FSX)
# License: GPL v3, see the COPYING file for details
# Rewritten using requests library for SNI support, Spencer Julian, 2015
# =============================================================================

import requests
import urllib
#import xbmc #For Logging
  
class Request():
  
    def __init__(self, config):
        self.username, self.password, self.host, self.user_agent = config
  
    def set_auth():
        pass
  
    def retrieve(self, url):
  
        try:
            filename, headers = urllib.urlretrieve(url)
        except urllib.ContentTooShortError:
            return False
        else:
            return (filename, headers)
  
    def execute(self, path, params=None, method='GET', authenticate=False, ssl=False):
  
        headers = {'User-Agent': self.user_agent}
  
        if method == 'POST' or method == 'PUT':
            headers['Content-type'] = 'application/x-www-form-urlencoded'

        protocol = "https://" if ssl else "http://"

        if authenticate:
            response = requests.request(method.upper(), protocol + self.host + '/' + path, params=params, headers=headers, auth=(self.username, self.password))
        else:
            response = requests.request(method.upper(), protocol + self.host + '/' + path, params=params, headers=headers)

	if 200 <= response.status_code < 300:
            response_content = response.text
        else:
            raise HttpStatusError()
          
        return response_content
          
class HttpStatusError(Exception):
    pass
