# lists.py ---
#
# Filename: lists.py
# Description: NationBuilder Lists API access
# Author: Niklas Rehfeld
#
#    Copyright 2014 Niklas Rehfeld
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

from nb_api import NationBuilderApi

import json
import logging


class Lists(NationBuilderApi):

    """
    Class for accessing NationBuilder Lists API endpoints.
    """

    def __init__(self, nation_slug, api_key):
        super(Lists, self).__init__(nation_slug, api_key)
        self.logger = logging.getLogger(__name__)

    def list_lists(self, per_page=100):
        """
        Get all of the lists in the nation.
        """
        res = self._list_list_page(page=1, per_page=per_page)
        jres = json.loads(res)
        i = 2
        while i <= jres['total_pages']:
            self.logger.debug("getting page %i of %i", i, jres['total_pages'])
            more = self._list_list_page(page=i, per_page=per_page)
            jmore = json.loads(more)
            jres['results'].extend(jmore['results'])
            jres['total'] += jmore['total']
            i += 1
        # make the total number of pages = 1, as we've merged all the pages.
        jres['total_pages'] = 1
        jres['per_page'] = jres['total']
        self.logger.debug("lists: %s", jres)
        return jres

    def _list_list_page(self, page=1, per_page=100):
        """Gets a list of nb_lists available in NB Will do a max of 100."""
        self._authorise()
        url = self.LIST_INDEX_URL.format(page=page, per_page=per_page)
        hdr, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(hdr, content, url)
        return content

    def get_list_page(self, list_id, page_num=1, per_page=50):
        """
        Gets a single page of results of a list.

        Parameters:
            list_id: the ID of the list.
            page_num: the page number (>= 1)
            per_page: the number of entries to show per page. (<= 100)
            """
        self._authorise()
        url = self.GET_LIST_URL.format(
            list_id=list_id, per_page=per_page, page=page_num)
        header, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(header, content, url)
        return json.loads(content)

    def get_list(self, list_id, per_page=50):
        """
        Gets the people in a list.
        Can take a very long time, as it concatenates all of the pages.

        returns a json array of person records."""
        # TODO make it a bit more efficient somehow.
        self._authorise()
        page = 1
        lists = []  # Make it a set to avoid duplicates.
        while True:
            url = self.GET_LIST_URL.format(list_id=list_id,
                                           per_page=per_page, page=page)
            header, content = self.http.request(url, headers=self.HEADERS)
            self._check_response(header, content, "Get list", url)
            content = json.loads(content)
            lists.extend(content['results'])
            page += 1
            if page > content['total_pages']:
                break

        self.logger.debug("retrieved %d people", len(lists))
        return lists

    def get_list_iter(self, list_id, per_page=100):
        """
        Generator function that gets the people in a list. may be more
        efficient than get_list() in some cases.
        """
        self._authorise()
        page = 1
        while True:
            url = self.GET_LIST_URL.format(list_id=list_id,
                                           per_page=per_page, page=page)
            header, content = self.http.request(url, headers=self.HEADERS)
            self._check_response(header, content, "Get list", url)
            content = json.loads(content)
            for person in content['results']:
                yield person
            page += 1
            if page > content['total_pages']:
                break
