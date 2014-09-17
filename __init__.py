# __init__.py ---
#
# Filename: __init__.py
# Description: NationBuilder API Library
# Author: Niklas Rehfeld
# Copyright 2014 Niklas Rehfeld
# URL: https://github.com/nikr/nbpy
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Package nbpy:

Contains the following modules:

nb_api: contains the NationBuilderApi class, which is used as a base class for
    the various APIs -- People, Tags, Lists, etc. It also contains the
    Exception classes that are raised by the API access methods.

nationbuilder: Contains the NationBuilder class which serves as the main entry
    point for this library. It is recommended to instantiate one of these and
    use the NationBuilder.people, NationBuilder.tags, etc. members to access
    the various APIs.

people: Contains the People class, used to access the People API.

tags: Contains the Tags class used to access the Tags API

lists: Contains the NBLists class used to access the Lists API.

This file also includes the definitions for various URLs used to access the
various NationBuilder APIs.

"""

BASE_URL = 'https://{slug}.nationbuilder.com/api/v1'
PAGINATE_QUERY = "?page={page}&per_page={per_page}"
GET_PERSON_URL = BASE_URL + '/people/{0}'
MATCH_EMAIL_URL = BASE_URL + "/people/match?email={0}"
UPDATE_PERSON_URL = GET_PERSON_URL
REMOVE_TAG_URL = UPDATE_PERSON_URL + "/taggings/{1}"
LIST_TAGS_URL = BASE_URL + "/tags" + PAGINATE_QUERY
GET_BY_TAG_URL = BASE_URL + "/tags/{tag}/people" + PAGINATE_QUERY
REGISTER_PERSON_URL = GET_PERSON_URL + "/register"

LIST_INDEX_URL = BASE_URL + '/lists' + PAGINATE_QUERY
GET_LIST_URL = BASE_URL + '/lists/{list_id}/people' + PAGINATE_QUERY

GET_CONTACT_URL = GET_PERSON_URL + "/contacts"

USER_AGENT = "nbpy/0.2"

HEADERS = {
    'Content-type': 'application/json',
    "Accept": "application/json",
    "User-Agent": USER_AGENT,
}
