
import logging
import urllib
import urllib2

from exceptions import Exception


def _py26OrGreater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26OrGreater():
    import json
else:
    import simplejson as json

class GeoApiError(Exception):
    """
    Base Exception thrown by the GeoApi object when there is a
    general error interacting with the API.
    """
    pass

class GeoApiHTTPError(GeoApiError):
    """
    Exception thrown by the GeoApi object when there is an
    HTTP error interacting with http://developer.yahoo.com/geo/geoapi/.
    """
    def __init__(self, e, uri, format, encoded_args):
      self.e = e
      self.uri = uri
      self.format = format
      self.encoded_args = encoded_args

    def __str__(self):
        return (
            "GeoApi sent status %i for URL: %s.%s using parameters: "
            "(%s)\ndetails: %s" %(
                self.e.code, self.uri, self.format, self.encoded_args, 
                self.e.fp.read()))

class GeoApiCall(object):
    def __init__(self, appid, format, domain, uri="", encoded_args=None):
        self.appid = appid
        self.format = format
        self.domain = domain
        self.uri = uri
        self.encoded_args = encoded_args

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            return GeoApiCall(self.appid, self.format, self.domain, self.uri + "/" + k, self.encoded_args)

    def __call__(self, **kwargs):
        uri = self.uri.strip("/")
        method = "GET"

        uriBase = "http://%s/%s" %(self.domain, uri)

        if kwargs.has_key('filter'):
            uriBase += ".%s" %(kwargs['filter'])
        
        urlArgs = {"format":self.format, "appid":self.appid}
        if self.encoded_args:
            urlArgs.update(self.encoded_args)
        argStr = "?%s" % (urllib.urlencode(urlArgs))
        
        argData = None
        headers = {}

        print(uriBase+argStr)
        logging.error(uriBase+argStr)
        req = urllib2.Request(uriBase+argStr, argData, headers)
        
        try:
            handle = urllib2.urlopen(req)
            if "json" == self.format:
                return json.loads(handle.read())
            else:
                return handle.read()
        except urllib2.HTTPError, e:
            if (e.code == 304):
                return []
            else:
                raise GeoApiHTTPError(e, uri, self.format, self.encoded_args)

class GeoApi(GeoApiCall):
    """
    The minimalist yet fully featured GeoApi API class.

    Get RESTful data by accessing members of this class. The result
    is decoded python objects (lists and dicts).

    The GeoApi API is documented here:

      http://developer.yahoo.com/geo/geoapi/guide/

    Examples::

      geoapi = GeoApi(appid=[yourappidhere])

      # Get all countries
      geoapi.countries()
      
      # Get all US states
      geoapi.states.US()
      
      # Get Place
      geoapi.place.woeid_2507854()


    Using the data returned
    -----------------------

    GeoApi API calls return decoded JSON. This is converted into
    a bunch of Python lists, dicts, ints, and strings. For example::

      x = geoapi.countries()

      # The number of countries
      x['places']['count']


    Getting raw XML data
    --------------------

    If you prefer to get your GeoApi data in XML format, pass
    format="xml" to the GeoApi object when you instantiate it::

      geoapi = GeoApi(appid=[yourappidhere], format="xml")

      The output will not be parsed in any way. It will be a raw string
      of XML.

    """
    def __init__(self, format="json", domain="api.geoapi.com", apikey=None, api_version='v1'):
        """
        Create a new GeoApi API connector.

        `domain` lets you change the domain you are connecting. By
        default it's where.yahooapis.com.

        `api_version` is used to set the base uri. By default it's 'v1'.
        """
        
        if (format not in ("json", "geojson", "xml", "")):
            raise ValueError("Unknown data format '%s'" %(format))

        uri = ""
        if api_version:
            uri = api_version

        GeoApiCall.__init__(self, appid, format, domain, uri)

        
        

__all__ = ["GeoApi", "GeoApiError", "GeoApiHTTPError"]
