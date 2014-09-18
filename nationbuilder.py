# nationbuilder.py ---
#
# Filename: nationbuilder.py
# Description: Main Entry point.
# Author: Niklas Rehfeld

"""
The  NationBuilder object is used as a way of accessing a NationBuilder Nation.
It contains attributes for accessing the various API endpoints.

Example usage:

# create a NationBuilder object that accesses the slug.nationbuilder.com nation
my_site = nbpy.nationbuilder.NationBuilder("slug", MY_API_KEY)

# get person with ID=123
ppl = my_site.people.get_person(123)

# retrieve the people in list 5
list_five = my_site.lists.get_list(5)

"""
from people import People
from tags import NBTags
from lists import Lists


class NationBuilder(object):
    """
    Entry point to nationbuilder APIs.

    Public attributes:
        people : nbpy.people.People instance for accessing people API
        tags : nbpy.tags.NBTags instance for accessing People Tags API
        lists : nbpy.lists.NBList instance for accessing Lists API
    """
    def __init__(self, slug, api_key):
        super(NationBuilder, self).__init__()

        self.people = People(slug, api_key)
        self.tags = NBTags(slug, api_key)
        self.lists = Lists(slug, api_key)
