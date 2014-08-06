"""Contains functions for getting at the NationBuilder API."""

#import test
import httplib2
import urllib2
import logging
import json
from oauth2client.client import AccessTokenCredentials


class NationBuilder(object):
    """Interface to the NationBuilder API."""
    NATION_SLUG = None
    BASE_URL = 'https://' + NATION_SLUG + '.nationbuilder.com/api/v1'
    PAGINATE_QUERY = "?page={page}&per_page={per_page}"
    GET_PERSON_URL = BASE_URL + '/people/{0}'
    MATCH_EMAIL_URL = BASE_URL + "/people/match?email={0}"
    UPDATE_PERSON_URL = GET_PERSON_URL
    REMOVE_TAG_URL = UPDATE_PERSON_URL + "/taggings/{1}"
    LIST_TAGS_URL = BASE_URL + "/tags" + PAGINATE_QUERY
    GET_BY_TAG_URL = BASE_URL + "/tags/{tag}/people" + PAGINATE_QUERY
    REGISTER_PERSON_URL = GET_PERSON_URL + "/register"

    ACCESS_TOKEN = None
    USER_AGENT = "nbpy/0.1"
    HEADERS = {'Content-type': 'application/json', "Accept": "application/json"}

    http = None
    
    def __init__(self, slug, token):
        """Create a NationBuilder Connection.
        
        Parameters:
            slug : String - the nation slug (e.g. foo if your nation is at foo.nationbuilder.com) 
            token : String - the access token or test token from nationbuilder """
            
        self.NATION_SLUG = slug
        self.ACCESS_TOKEN = token

    def _authorise(self):
        """Gets AccessTokenCredentials with the ACCESS_TOKEN and USER_AGENT and
        authorises a httplib2 http object.
        
        If this has already been done, does nothing."""
        if self.http is not None:
            return
        if self.ACCESS_TOKEN is None:
            logging.error("No Access Token supplied.")
        cred = AccessTokenCredentials(self.ACCESS_TOKEN, self.USER_AGENT)
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)
        self.http = cred.authorize(self.http)

    def get_person(self, person_id):
        """returns the json string of the person with id person_id.
        if not found, returns None """
        self._authorise()
        url = self.GET_PERSON_URL.format(urllib2.quote(str(person_id)))
        response, content = self.http.request(url, headers=self.HEADERS)
        _log_response(response, content, url)
        if response['status'] != '200':
            return None
        return content


    def get_people_by_tag(self, tag, tags_per_page=100):
        """ get a list of people by tag.
        returns json array of people"""
        self._authorise()
        page = 1
        url = self.GET_BY_TAG_URL.format(tag=str(tag),
                                        page=page,
                                        per_page=str(tags_per_page))
        header, content = self.http.request(url, headers=self.HEADERS)
        _log_response(header, content, url)
        content = json.loads(content)
        people = content['results']
        num_pages = content['total_pages']
        while page < num_pages:
            page += 1
            url = self.GET_BY_TAG_URL.format(tag=str(tag),
                                             page=page,
                                             per_page=str(tags_per_page))
            header, content = self.http.request(url, headers=self.HEADERS)
            _log_response(header, content, url)
            content = json.loads(content)
            people.extend(content['results'])
        return people


    def get_tags(self, person_id):
        """Gets all of the tags that a person is tagged with.
        
        Parameters:
            person_id : The NationBuilder ID of the person to query.
            
        Returns:
            a (possibly empty) list of tags or None if person doesn't exist. """
        person = self.get_person(person_id)
        if person is None:
            return None
        return json.loads(person)['person']['tags']

    def _get_list_tags_page(self, tags_per_page, page_num):
        """gets a page of results of the tag list"""
        self._authorise()
        url = self.LIST_TAGS_URL.format(page=str(page_num),
                                        per_page=str(tags_per_page))
        header, content = self.http.request(url, headers=self.HEADERS)
        _log_response(header, content, url)
        return json.loads(content)


    def list_tags(self, tags_per_page=100):
        """ Gets all of the tags that are defined in the nation
        
        Parameters: 
            tags_per_page : how many tags to fetch per call, maximum. Defaults to 100
          
        Returns: 
            a list of tags.
        """

        page = self._get_list_tags_page(tags_per_page, 1)
        tags = page['results']
        total_pages = page['total_pages']
        current_page = page['page']
        while total_pages > current_page:
            current_page += 1
            next_page = self._get_list_tags_page(tags_per_page, current_page)
            tags.extend(next_page['results'])
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
        hdr, cnt = self.http.request(url, method="DELETE", headers=self.HEADERS)
        if hdr['status'] != '204':
            logging.warning("Expected 204: No content, but got %s", hdr)


    def update_person(self, person_id, update_str):
        """Update a person's record.
        parameters:
          person_id - the person's NB id.
          update_str - string of json representation of the modifications
          to be made to that person e.g.
          {
            "person": {
            "first_name": "Joe",
            "email": "johndoe@gmail.com",
            "phone": "303-555-0841"}
          }
        """
        self._authorise()
        #person_str = json.dumps(person_json)
        url = self.UPDATE_PERSON_URL.format(urllib2.quote(str(person_id)))
        header, content = self.http.request(url, method="PUT",
                                            body=update_str,
                                            headers=self.HEADERS)
        _log_response(header, content, url)
        if header['status'] != '200':
            return None
        return content

    def set_recruiter_id(self, person_id, recruiter_id):
        """convenience method to set a recruiter id.
        
        Parameters:
            person_id : the NationBuilder ID of the person whose recruiter is being set
            recruiter_id : the NationBuilder ID of the recruiter
        
        returns same as update_person()"""
        update_string = """ { "person": {"recruiter_id":"""
        update_string += str(recruiter_id) + "}} "
        # update_string.format(str(recruiter_id))
        return self.update_person(person_id, update_string)

    def set_volunteer(self, person_id, volunteer=True):
        """Convenience method to make a person a volunteer.
        
        Parameters: 
            person_id : NationBuilder ID of the person to make a volunteer
            volunteer : Set to True if they are a volunteer, False if they are not. defaults to True
            
        returns the same as update_person()"""
        update_string = """ {"person":{ "is_volunteer": """
        if volunteer:
            update_string += 'true'
        else:
            update_string += 'false'
        update_string += '}}'
        return self.update_person(person_id, update_string)

    def get_person_by_email(self, email):
        """returns the first person that has a given email address.
        
        Parameters: 
            email : the email address to look for.
            
        Returns: 
            A JSON string of the person.
        
        """
        self._authorise()
        url = self.MATCH_EMAIL_URL.format(urllib2.quote(email))
        header, content = self.http.request(url, headers=self.HEADERS)
        _log_response(header, content, url)
        if header['status'] != '200':
            return None
        return content

    def get_id_by_email(self, email):
        """wrapper around get_person_by_email() that just returns the NB ID.
        or None if not found."""
        person = self.get_person_by_email(email)
        if person is None:
            return None
        return json.loads(person)['person']['id']

    def set_page_slug(self, nb_id, slug):
        """sets the site slug of the person
        is a wrapper around update_person()
        For some reason it doesn't work though. Might be an API problem."""
        update_str = ' {"person": {"page_slug" :" ' + slug + '"}}'
        
        return self.update_person(nb_id, update_str)
    
    def do_registration(self, nb_id):
        """Causes NB to send the registration email to the person. 
        
        Parameters: 
            nb_id : NationBuilder ID of the person to send registration email to."""
        self._authorise()
        url = self.REGISTER_PERSON_URL.format(urllib2.quote(nb_id))
        hdr,content = self.http.request(url, headers=self.HEADERS)
        _log_response(hdr, content, url)


def _log_response(headers, content, url=None):
    """Log a warning if this is not a 200 OK response,
    otherwise log the response at debug level"""
    if headers['status'] != '200':
        if url is not None:
            logging.warn("Request to URL: %s is not ok.", url)
        else:
            logging.warn("Request is not ok.")
        logging.warn("Got reply status: %s, content: %s", headers['status'], content)
    else:
        if url is not None:
            logging.debug("Request to %s successful.", url)
        else:
            logging.debug("Request successful.")
