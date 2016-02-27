# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from time import sleep
import requests
import lxml.etree


class GeoNamesGeocoder(object):
    ENDPOINT = 'http://api.geonames.org'
    USERNAME = 'russss'

    def __init__(self):
        self.session = requests.Session()

    def geocode(self, latitude, longitude):
        data = self.find_nearby(latitude, longitude)
        if data is None:
            return None, None

        if data.find('ocean') is not None:
            # We're over an ocean
            return "over the", data.find('ocean/name').text
        elif data.find('country') is not None:
            # No populated places nearby, but we have a country
            country_name = data.find('countryName').text
        elif data.find('address') is not None:
            country_name = data.find('address/countryName').text
        elif len(data.findall('geoname')) > 0:
            continent_node = data.findall('geoname')[1]
            country_name = continent_node.find('name').text
        return "over", country_name

    def find_nearby(self, latitude, longitude, radius=10):
        params = {'lat': latitude, 'lng': longitude,
                  'cities': 'cities15000', 'username': self.USERNAME}
        if radius is not None:
            params['range'] = radius

        result = self.session.get('%s/extendedFindNearby' % self.ENDPOINT, params=params, timeout=10).content

        data = lxml.etree.fromstring(result)

        error = data.find('status')
        if error is not None:
            value = error.get('value')
            if value == '24' and radius > 1:
                # In some areas of the world, geonames restricts our radius, so try without.
                return self.find_nearby(latitude, longitude, radius=None)
            elif value == '19':
                print("Hourly rate limit exceeded. Sleeping for 5mins.")
                sleep(300)
                return self.find_nearby(latitude, longitude, radius=radius)
            elif value == '18':
                raise Exception("Daily rate limit exceeded!")
            elif value == '12':
                print("Unknown Geonames error, sleeping for 10 seconds")
                sleep(10)
                return None
            else:
                raise Exception("Unhandled Geonames error: %s" % value)
        return data
