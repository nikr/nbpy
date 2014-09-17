"""
Functionality from the NationBuilder People API.

classes:
    People
     -- Used to access the People API.

"""

from nb_api import NationBuilderApi
import urllib2
import json


class People(NationBuilderApi):

    """
    Used to get at the People API

    See http://nationbuilder.com/people_api for info on the data returned
    """

    def __init__(self, slug, token):
        super(People, self).__init__(slug, token)

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
        url = self.GET_PERSON_URL.format(person_id)
        headers, content = self.http.request(url, headers=self.HEADERS)
        self._check_response(headers, content, "Get Person", url)
        return json.loads(content)

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

    def match_person(self, **kwargs):
        """
        Match a person by criteria.

        This will return a person that matches one or more criteria exactly,
        and it is a unique match. If there is no match, or there are multiple
        matches, it will raise an exception.

        The keyword arguments can be 'email', 'first_name', 'last_name',
        'phone', or 'mobile'.
        """
        self._authorise()
        query_string = '&'.join([key + '=' + kwargs[key] for key in
                                 kwargs.keys])
        url = self.MATCH_PERSON_URL + query_string
        hdr, cnt = self.http.request(url, headers=self.HEADERS)
        self._check_response(hdr, cnt, "Match %s" % kwargs, url)
        return json.loads(cnt)

    def get_person_by_email(self, email):
        """Returns the first person that has a given email address.

        Parameters:
            email : the email address to look for.

        Returns: A person record or None if no match.
        """
        self._authorise()
        url = self.MATCH_EMAIL_URL.format(urllib2.quote(email))
        header, content = self.http.request(url, headers=self.HEADERS)
        if header.status == 400:
            if json.loads(content)['code'] == 'no_matches':
                return None
            else:
                self._check_response(header, content,
                                     "Get person by email", url)
        elif header.status == 200:
            return json.loads(content)
        else:
            self._check_response(header, content, "Get person by email", url)

    def get_id_by_email(self, email):
        """
        wrapper around get_person_by_email().

        Returns: the NB ID or None if not found.
        """
        person = self.get_person_by_email(email)
        if person is None:
            return None
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
