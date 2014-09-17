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


"""
