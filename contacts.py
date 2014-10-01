# contacts.py ---
#
# Filename: contacts.py
# Description: Module for accessing the NationBuilder Contacts API.
# Author: Niklas Rehfeld
#
#    Copyright (c) 2014 Niklas Rehfeld
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

import nb_api
import json


class Contacts(nb_api.NationBuilderApi):

    def __init__(self, nation_slug, api_key):
        super(Contacts, self).__init__(nation_slug, api_key)

    def log_contact(self, nb_id, contact_type, contact_method, sender_id,
                    status=None, broadcaster=None, note=None):
        """
        Log a contact.

        Required Parameters:
            nb_id : The NationBuilder ID of the person who was contacted.
            contact_type : The contact type id. (see get_contact_types() ).
            contact_method : The contact method name.
            sender_id : The NationBuilder ID of the person who contacted them.
        Optional Parameters:
            status : The status (result) of the contact.
            broadcaster : The ID of the broadcaster this was on behalf of.
            note : Any additional notes to be logged.

        Returns:
            a dict-like contact response. e.g.
        {
        "contact": {
        "recipient_id": 4123,
        "sender_id": 1058,
        "broadcaster_id": 10,
        "status": "not_interested",
        "method": "door_knock",
        "type_id": 5,
        "note": "He did not support the cause",
        "created_at": "2014-02-14T14:36:29-05:00"
        }
        }
        """
        self._authorise()
        url = self.GET_CONTACT_URL.format(nb_id)
        update = {
            "contact": {
                "sender_id": sender_id,
                "method": contact_method,
                "type_id": contact_type,
            }
        }
        if broadcaster is not None:
            update['contact']['broadcaster_id'] = broadcaster
        if status is not None:
            update['contact']['status'] = status,
        if note is not None:
            update['contact']['note'] = note

        update = json.dumps(update)
        print str(update)

        header, content = self.http.request(url, headers=self.HEADERS,
                                            method='POST', body=str(update))
        self._check_response(header, content, "Log Contact", url)
        return json.loads(content)

    def get_person_contacts(self, nb_id, per_page=100):
        """
        Get all contacts for a person.

        Parameters:
            nb_id : the NationBuilder ID of the person.
            per_page : the number of contacts to fetch at once.

        Returns a list of contacts. 
        """
        base_url = self.GET_CONTACT_URL.format(nb_id) + self.PAGINATE_QUERY
        
        def get_person_contact_page(page):
            self._authorise()
            url = base_url.format(page=page, per_page=per_page)
            header, content = self.http.request(uri=url, headers=self.HEADERS)
            self._check_response(header, content, "Get Person Contact page", url)
            return json.loads(content)

        first_page = get_person_contact_page(1)
        total_pages = first_page['total_pages']
        result = first_page['results']
        for page_no in range(2, total_pages + 1):
            result += get_person_contact_page(page_no)['results']

        return result

    def list_contact_types(self):
        """
        Returns a list of contact types defined in this nation.
        """
        raise NotImplementedError("get_contact_types is not yet implemented.")
        

    def create_contact_type(self, name):
        """
        Create a new contact type.

        Parameters:
            name : the name of the contact type.

        Returns a dict like
        {
        "contact_type": {"name": "new type name", 'id' : 21}
        }

        """
        raise NotImplementedError()

    def update_contact_type(self, type_id, name):
        """
        update the name of a contact type.

        Parameters:
            type_id : the id of the contact type.
            name : the new name for the contact type.
        """
        raise NotImplementedError()

    def delete_contact_type(self, type_id):
        """
        Delete a contact type.

        Parameters:
            type_id : the id of the contact type to delete.

        Returns nothing.
        """
        raise NotImplementedError()

    def list_contact_methods(self):
        """
        List the contact methods available.
        
        Returns a list of contact method entries, which look like
        {'name' : 'Foo Bar', 'api_name' : 'foo_bar'}
        """
        raise NotImplementedError()
        
    def list_contact_statuses(self):
        """
        List the contact statuses available.
        
        Returns a list of contact status entries, which look like
        {'name': 'Bad Info', 'api_name': 'bad_info'}
        """
        raise NotImplementedError()
