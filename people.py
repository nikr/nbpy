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

    def update_person(self, person_id, update_body):
        """
        Update a person's record with arbitrary info.

        Note that not all fields in a person record can be written.

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
        if isinstance(update_body, str):
            update_str = update_body
        else:
            update_str = json.dumps(update_body)
        header, content = self.http.request(url, method="PUT",
                                            body=update_str,
                                            headers=self.HEADERS)
        self._check_response(header, content,
                             "Update person with id %d" % person_id, url)
        return json.loads(content)

    def create_person(self, person_body):
        """
        Create a person.
        A person is considered valid with a name, a phone number or an email.

        Parameters:
            person_body : The body of the person to create. e.g.
        {
            "person":
            {
                "email": "bob@example.com",
                "last_name": "Smith",
                "first_name": "Bob",
                "sex": "M",
                "employer": "Dexter Labs",
                "party": "P",
                "registered_address": {
                    "state": "TX",
                    "country_code": "US"
                }
            }
        }

        Returns a dict-like representation of the person's complete record.
        """
        self._authorise()
        url = self.GET_PEOPLE_URL
        header, content = self.http.request(uri=url, headers=self.HEADERS,
                                            method='POST')
        self._check_response(header, content, "Create person", url)
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

        To find people that have non-unique attributes, use search()
        """
        self._authorise()
        # turn the kwargs into url-style ones. k1=v1&k2=v2...
        keyvals = ['='.join((urllib2.quote(key), urllib2.quote(val)))
                   for key, val in kwargs.iteritems()]
        query_string = '&'.join(keyvals)
        url = self.MATCH_PERSON_URL + query_string
        hdr, cnt = self.http.request(url, headers=self.HEADERS)
        self._check_response(hdr, cnt, "Match %s" % kwargs, url)
        return json.loads(cnt)

    def search(self, per_page=100, **kwargs):
        """
        Find people that have certain attributes.

        Parameters:
            per_page : the number of people to fetch at a time.
            kwargs : attributes to search for. Allowable keys are:
                first_name, last_name, city, state, sex, birthdate,
                updated_since, with_mobile, civicrm_id, county_file_id,
                state_file_id, datatrust_id, dw_id, media_market_id,
                membership_level_id, ngp_id, pf_strat_id, van_id,
                salesforce_id, rnc_id, rnc_regid, external_id,
                custom_values (as a string).

        See http://nationbuilder.com/people_api "Search Endpoint" for details.

        Returns a list of abbreviated person records.
        """
        self._authorise()
        keyvals = ['='.join((urllib2.quote(key), urllib2.quote(val)))
                   for key, val in kwargs.iteritems()]
        query = self.SEARCH_PERSON_URL + '&' + '&'.join(keyvals)

        def get_search_page(page):
            url = query.format(page=page, per_page=per_page)
            hdr, cnt = self.http.request(uri=url, headers=self.HEADERS)
            self._check_response(hdr, cnt, "Search %s" % keyvals, url)
            return json.loads(cnt)

        first_page = get_search_page(1)
        total_pages = first_page['total_pages']
        result = first_page['results']
        for page_no in xrange(2, total_pages + 1):
            result += get_search_page(page_no)['results']

        return result

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

    def delete_person(self, nb_id):
        """
        Deletes the person with the given ID.

        Parameters:
            nb_id : The id of the person to delete.

        Returns:
            None
        """
        self._authorise()
        url = self.GET_PERSON_URL.format(str(nb_id))
        hdr, cnt = self.http.request(uri=url, method="DELETE",
                                     headers=self.HEADERS)
        self._check_response(hdr, cnt, "Delete user %d" % nb_id, url)

    def get_people_iter(self, per_page=100):
        """
        Retrieves all people in the nation.

        This is implemented as a generator function, as the amount of data
        returned can be pretty big.

        Parameters:
            per_page : the number of people to fetch at a time.
                0 < per_page <= 100

        Note that the returned people records are abbreviated records. To get
        the full record use get_person() with the NB ID from this record.
        """
        # TODO: it would be nice to fetch the next page asynchronously
        # before it is needed.
        def get_people_page(page):
            self._authorise()
            url = self.GET_PEOPLE_URL + self.PAGINATE_QUERY.format(
                page=page, per_page=per_page)
            hdr, cnt = self.http.request(uri=url, headers=self.HEADERS)
            self._check_response(hdr, cnt, "Get people page %d" % page, url)
            return json.loads(cnt)
        # need to get the first page before to see the range
        page = get_people_page(1)
        total_pages = page['total_pages']
        # loop starts at 2 because we already have the first page.
        for current_page in xrange(2, total_pages + 1):
            for person in page['results']:
                yield person
            page = get_people_page(current_page)

    def get_nearby(self, lat, lng, dist, use_km=False, per_page=100):
        """
        Fetches all people within a radius of dist miles of the
        coordinates (lat,lng).

        Parameters:
            lat : latitude of the coordinate in WGS84
            lng : longitude of the coordinate
            dist : radius to search. (default in miles, see use_metric)
            use_km : set to True if dist is in kilometers
            per_page : number of records to fetch at a time

        Returns:
            a list of people records.
        """
        self._authorise()
        km = 0.621371
        if use_km:
            dist = dist * km

        def get_nearby_page(page):
            url = self.NEARBY_URL.format(lat=lat, lng=lng, dist=dist,
                                         per_page=per_page, page=page)
            hdr, cnt = self.http.request(uri=url, headers=self.HEADERS)
            self._check_response(hdr, cnt, "Get nearby", url)
            return json.loads(cnt)

        first_page = get_nearby_page(1)
        total_pages = first_page['total_pages']
        result = first_page['results']
        for p in xrange(2, total_pages + 1):
            result += get_nearby_page(p)

        return result

    
    def me(self):
        """Fetches the Access token owner's profile"""
        self._authorise()
        url = self.GET_PEOPLE_URL + '/me'
        hdr, cnt = self.http.request(uri=url, headers=self.HEADERS)
        self._check_response(hdr, cnt, 'Get Me', url)
        return json.loads(cnt)
        
