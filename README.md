nbpy
====

A Python interface to NationBuilder API

This is very much a work in progress, so only parts of the API are supported (mainly the People endpoints). As it is a work in progress, expect major changes in the library in the not-too-distant future. So if you do build something on top of this library now, it may or may not work in the next version. 


It relies on jcgregorio/httplib2@master and [oauth2client](https://code.google.com/p/google-api-python-client/wiki/OAuth2Client). These are used because the original use of this was running on GAE. 

They can both be installed using pip, as far as I know.

It also uses the builtin `json`, `urllib2` and `logging` modules. 

Example Usage: 

```python
import nationbuilder
import json

# connect to foo.nationbuilder.com People API
nb_people = nationbuilder.People('foo', 'FFAACC1123344556677889900')
# get steve's (NationBuilder ID = 123)  details
steve = people.get_person(123)
print "First Name: %s" % steve['person']['first_name']
```

