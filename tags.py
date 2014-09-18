# tags.py ---
#
# Filename: tags.py
# Description:  Access to the Tags API
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
#

"""
People Tags API. See http://nationbuilder.com/people_tags_api for more details.
"""

import urllib2
from nb_api import NationBuilderApi
import json


class NBTags(NationBuilderApi):

    def __init__(self, slug, token):
        super(NBTags, self).__init__(slug, token)

    def get_people_by_tag(self, tag, per_page=100):
        """
        Get a list of all the people with a tag.

        Parameters:
            tag: the tag to look for. Cannot contain '/' characters.
                 The tag is case sensitive.
            tags_per_page: the number of tags to get at once (default 100)
                 per_page must be in the range 0 < per_page <= 100

        Returns:
            a list of people records.
        """
        self._authorise()
        page = 1
        url = self.GET_BY_TAG_URL.format(tag=urllib2.quote(str(tag), ''),
                                         page=page,
                                         per_page=str(per_page))
        header, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(header, content, "Get people by tag", url)
        content = json.loads(content)
        people = content['results']
        num_pages = content['total_pages']
        while page < num_pages:
            page += 1
            url = self.GET_BY_TAG_URL.format(tag=str(tag),
                                             page=page,
                                             per_page=str(per_page))
            header, content = self.http.request(url, headers=self.HEADERS)
            self._check_response(header, content, "Get people by tag", url)
            content = json.loads(content)
            people.extend(content['results'])
        return people

    def get_person_tags(self, person_id):
        """
        Get a complete list of all the taggings for a given person.

        Parameters:
            person_id : The NationBuilder ID of the person to query.

        Returns:
            a (possibly empty) list of tags.
        """
        # person = self.get_person(person_id)
        # return json.loads(person)['person']['tags']
        self._authorise()
        url = self.PERSON_TAGS_URL.format(str(person_id))
        headers, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(headers, content, "Get Person Tags", url)
        return json.loads(content)['taggings']

    def list_tags(self, tags_per_page=100):
        """
        Show the tags that have been used before in a nation.
        Parameters:
            tags_per_page : how many tags to fetch per call, maximum.
                Defaults to 100

        Returns:
            a list of tags.
        """
        def get_list_tags_page(tags_per_page, page_num):
            # gets a page of results of the tag list
            self._authorise()
            url = self.LIST_TAGS_URL.format(page=str(page_num),
                                            per_page=str(tags_per_page))
            header, content = self.http.request(url, headers=self.HEADERS)
            self._check_response(header, content, "Get tags page", url)
            return json.loads(content)

        page = get_list_tags_page(tags_per_page, 1)
        tags = [tag['name'] for tag in page['results']]
        total_pages = page['total_pages']
        current_page = page['page']
        while total_pages > current_page:
            current_page += 1
            next_page = get_list_tags_page(tags_per_page, current_page)
            tags.extend([tag['name'] for tag in next_page['results']])
        return tags

    def remove_tag(self, person_id, tag):
        """removes a tag from a person.

        Parameters:
            person_id : NationBuilder ID of the person to remove the tag from
            tag : the tag to remove.

        There is no response from this call, so this always returns None. """
        self._authorise()
        url = self.REMOVE_TAG_URL.format(urllib2.quote(str(person_id)),
                                         urllib2.quote(str(tag)))
        hdr, cnt = self.http.request(url, method="DELETE",
                                     headers=self.HEADERS)
        self._check_response(hdr, cnt,
                             "Remove Tag '%s' from id %d" % (tag, person_id),
                             url)

    def tag_person(self, nb_id, tag):
        """Tags a person with a tag."""
        self._authorise()
        url = self.PERSON_TAGS_URL.format(str(nb_id))
        body = {
            "tagging":
            {"tag": urllib2.quote(tag)}
        }
        hdr, cnt = self.http.request(url, method="PUT",
                                     headers=self.HEADERS,
                                     body=json.dumps(body))
        self._check_response(hdr, cnt,
                             "Tag %d with '%s'" % (nb_id, tag),
                             url)
        return json.loads(cnt)
        # TODO: check that the returned content includes the tag.
