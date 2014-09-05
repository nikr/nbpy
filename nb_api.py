# nb_api.py ---
#
# Filename: nb_api.py
# Description: Base functionality for the NationBuilder API
# Author: Niklas Rehfeld
# Copyright 2014 Niklas Rehfeld
# Created: Fri Sep  5 15:03:53 2014 (+1200)
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#

"""
Base functionality for the NAtionBuilder APIs.

Classes:
    NationBuilderAPI
     -- Base class of the other APIs.
    NBResponseError(Exception)
     -- Base Exception for non-200 server responses
    NBNotFoundError(NBResponseError)
     -- Exception signifying that the object (person/tag/etc.) that was queried
       was not found. Usually in response to a 404 response from the server.
    NBBadRequestError(NBResponseError)
     -- Exception signifying that the data sent to the server was bad. Usually
        in response to a 400 response from the server.
"""

import logging
import httplib2
from oauth2client import AccessTokenCredentials

log = logging.getLogger('nbpy')


class NationBuilderApi(object):
    def __init__(self, nation_slug, api_key):
        """Create a NationBuilder Connection.

        Parameters:
            slug : the nation slug (e.g. foo in foo.nationbuilder.com)
            token : the access token or test token from nationbuilder
        """

        self.NATION_SLUG = nation_slug
        self.ACCESS_TOKEN = api_key
        self.BASE_URL = ''.join('https://', self.NATION_SLUG,
                                '.nationbuilder.com/api/v1')
        self.PAGINATE_QUERY = "?page={page}&per_page={per_page}"

        self.USER_AGENT = "nbpy/0.2"

        self.HEADERS = {
            'Content-type': 'application/json',
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT,
        }

    def _authorise(self):
        """Gets AccessTokenCredentials with the ACCESS_TOKEN and USER_AGENT and
        authorises a httplib2 http object.

        If this has already been done, does nothing."""
        if self.http is not None:
            return
        assert self.ACCESS_TOKEN is not None

        # if cred.user_agent is not none, then it adds appends the
        # user-agent to the end of the existing user-agent string
        # each time request() is called...
        # ...Until you get a "headers too long" error.
        # so make it None
        cred = AccessTokenCredentials(self.ACCESS_TOKEN, None)

        # NationBuilder has a lot of problems with their SSL certs...
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)
        self.http = cred.authorize(self.http)

    def _check_response(self, headers, content, attempted_action, url=None):
        """Log a warning if this is not a 200 OK response,
        otherwise log the response at debug level"""
        if headers.status < 200 or headers.status > 299:
            self._raise_error(attempted_action, headers, content, url)
        else:
            log.debug("Request to %s successful.",
                      url or attempted_action or "Unknown")

    def _raise_error(self, msg, header, body, url):
        """Raises the correct type of exception."""
        error_map = {
            404: NBNotFoundError,
            400: NBBadRequestError
            }
        err = error_map.get(header.status) or NBResponseError
        raise err(msg, header, body, url)


class NBResponseError(Exception):
    """Base class for all non-200 OK responses.
    Includes the following additional fields:
    header: the response headers
    body: the response body
    url: the requested url.
    """
    def __init__(self, msg, header, body, url):
        self.url = url
        self.header = header
        self.body = body
        Exception.__init__(msg)


class NBBadRequestError(NBResponseError):
    """Indicates a bad request"""
    pass


class NBNotFoundError(NBResponseError):
    """Generally indicates that a 404 error was returned...
    contains the header and body of the server response."""
    pass
