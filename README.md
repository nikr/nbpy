# nbpy


## A Python interface to NationBuilder API
----------------------------------------
This is very much a work in progress, so only parts of the API are supported (mainly the People endpoints). As it is a work in progress, expect major changes in the library in the not-too-distant future. So if you do build something on top of this library now, it may or may not work in the next version. 

This library is entirely unofficial and not endorsed by nationbuilder.com in any way. 

It relies on [httplib2](https://github.com/jcgregorio/httplib2) and [oauth2client](https://code.google.com/p/google-api-python-client/wiki/OAuth2Client). These are used because the original use of this was running on GAE. 

They can both be installed using pip, as far as I know.

It also uses the builtin `json`, `urllib2` and `logging` modules. 


### Example Usage: 

```python
from nbpy import nationbuilder
import json

# connect to nationbuilder using a credentials file
nb = nationbuilder.from_file('credentials_file')
# get steve's (NationBuilder ID = 123)  details
steve = nb.people.get_person(123)
print "First Name: %s" % steve['person']['first_name']
```

## Notes: 
2015/01/13 
This library is currently not being developed, as I no longer have access to a NationBuilder instance for testing. Once I can get access to one I will resume develoment. If anyone has access to one I would be grateful for help.
