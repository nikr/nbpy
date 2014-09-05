"""
Functionality from the NationBuilder People API.

classes:
    People
     -- Used to access the People API.

"""

import NationBuilderApi
import urllib2
import json


class People(NationBuilderApi):

    """
    Used to get at the People API

    See http://nationbuilder.com/people_api for info on the data returned
    """

    def __init__(self, slug, token):
        super(People, self).__init__(slug, token)

        self.GET_PERSON_URL = self.BASE_URL + '/people/{0}'
        self.MATCH_EMAIL_URL = self.BASE_URL + "/people/match?email={0}"
        self.UPDATE_PERSON_URL = self.GET_PERSON_URL
        self.REMOVE_TAG_URL = self.UPDATE_PERSON_URL + "/taggings/{1}"
        self.LIST_TAGS_URL = self.BASE_URL + "/tags" + self.PAGINATE_QUERY
        self.GET_BY_TAG_URL = ''.join(self.BASE_URL, "/tags/{tag}/people",
                                      self.PAGINATE_QUERY)
        self.REGISTER_PERSON_URL = self.GET_PERSON_URL + "/register"

    def get_person(self, person_id):
        """
        Retrieves a person's record from NationBuilder.

        Parameters:
            person_id - The person's NationBuilder ID.

        Returns:
            A person record, as a dict.
        """
        self._authorise()
        # we need it as a string...
        person_id = urllib2.quote(str(person_id))
        url = self.GET_PERSON_URL.format()
        headers, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(headers, content, "Get Person", url)
        return json.loads(content)

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

    def get_tags(self, person_id):
        """Gets all of the tags that a person is tagged with.

        This is just a wrapper around get_person().

        Parameters:
            person_id : The NationBuilder ID of the person to query.

        Returns:
            a (possibly empty) list of tags.
        """
        person = self.get_person(person_id)
        return json.loads(person)['person']['tags']

    def list_tags(self, tags_per_page=100):
        """ Gets all of the tags that are defined in the nation

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

    def update_person(self, person_id, update_str):
        """
        Update a person's record with arbitrary info.

        Parameters:
            person_id - the person's NB id.
            update_str - string of json representation of the modifications
                to be made to that person e.g.
                {
                    "person": {
                    "first_name": "Joe",
                    "email": "johndoe@gmail.com",
                    "phone": "303-555-0841"}
                }

        Returns:
            the updated person record.
        """
        self._authorise()
        url = self.UPDATE_PERSON_URL.format(urllib2.quote(str(person_id)))
        header, content = self.http.request(url, method="PUT",
                                            body=update_str,
                                            headers=self.HEADERS)
        self._check_response(header, content,
                             "Update person with id %d" % person_id, url)
        return json.loads(content)

    def set_recruiter_id(self, person_id, recruiter_id):
        """
        Convenience method to set a recruiter id.

        Parameters:
            person_id : the NationBuilder ID of the person whose
                recruiter is being set
            recruiter_id : the NationBuilder ID of the recruiter

        Returns the updated person record.
        """
        update_string = """ { "person": {"recruiter_id":"""
        update_string += str(recruiter_id) + "}} "
        return self.update_person(person_id, update_string)

    def set_volunteer(self, person_id, volunteer=True):
        """Convenience method to make a person a volunteer.

        Parameters:
            person_id : NationBuilder ID of the person to make a volunteer
            volunteer : Set to True if they are a volunteer,
                False if they aren't. Defaults to True

        Returns the updated person record.
        """
        update_string = """ {"person":{ "is_volunteer": """
        if volunteer:
            update_string += 'true'
        else:
            update_string += 'false'
        update_string += '}}'
        return self.update_person(person_id, update_string)

    def get_person_by_email(self, email):
        """Returns the first person that has a given email address.

        Parameters:
            email : the email address to look for.

        Returns: A person record
        """
        self._authorise()
        url = self.MATCH_EMAIL_URL.format(urllib2.quote(email))
        header, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(header, content, "Get person by email", url)
        return json.loads(content)

    def get_id_by_email(self, email):
        """wrapper around get_person_by_email() that just returns the NB ID."""
        person = self.get_person_by_email(email)
        return person['person']['id']

    def do_registration(self, nb_id):
        """Causes NB to send the registration email to the person.

        Parameters:
            nb_id : NationBuilder ID of the person to register.

        Returns None
        """
        self._authorise()
        url = self.REGISTER_PERSON_URL.format(urllib2.quote(nb_id))
        hdr, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(hdr, content,
                             "Do registration for ID %d" % nb_id, url)
