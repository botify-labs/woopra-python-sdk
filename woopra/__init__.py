# -*- coding: utf-8 -*-

import urllib
import urllib2
import hashlib


class WoopraUnknownIdentifierException(Exception):
    """
    This exception is thrown when trying to identify() with an unsupported value.
    """
    pass


class WoopraUser(object):
    """
    This class represents a Woopra user's information.
    """

    def __init__(self, user_agent, ip_address, user_properties, email, cookie):
        self.user_properties = user_properties
        self.cookie = cookie
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.email = email


class WoopraTracker(object):
    """
    Woopra Python SDK.
    This class represents the Python equivalent of the JavaScript Woopra Object.
    """

    SDK_ID = "python"
    DEFAULT_TIMEOUT = 300000
    EMAIL = "email"
    UNIQUE_ID = "unique_id"
    BASE_URL = "http://www.woopra.com"

    def __init__(self, domain, access_key):
        """
        The constructor.
        Parameter:
            domain - str : the domain name of your website as submitted on woopra.com
            access_key - str : your woopra.com API access key
        Result:
            WoopraTracker
        """
        self.domain = domain
        self.idle_timeout = WoopraTracker.DEFAULT_TIMEOUT
        self.access_key = access_key

    def identify(self, identifier, value, user_properties={}, ip_address=None, user_agent=None):
        """
        Identifies a user.
        Parameters:
            identifier:
                WoopraTracker.EMAIL to identify the user with his email (will generate unique ID automatically with
                    a hash of the email)
                WoopraTracker.UNIQUE_ID to identify the user with a unique ID directly
            value - str : the value of the identifier (email or unique ID)
            user_properties (optional) - dict : the user's additional properties (name, company, ...)
                key - str : the user property name
                value -str, int, bool = the user property value
            ip_address (optional) - str : the IP address of the user.
            user_agent (optional) - str : the value of the user_agent header
        """
        if identifier == WoopraTracker.EMAIL:
            m = hashlib.md5()
            m.update(value)
            long_cookie = m.hexdigest().upper()
            cookie = (long_cookie[:12]) if len(long_cookie) > 12 else long_cookie
            return WoopraUser(user_agent, ip_address, user_properties, value, cookie)
        elif identifier == WoopraTracker.UNIQUE_ID:
            return WoopraUser(user_agent, ip_address, user_properties, None, value)
        raise WoopraUser

    def get_params(self, user_properties):
        """
        Returns GET parameters required in most Woopra HTTP requests
        Parameters:
            user_properties - WoopraUser : returned by call to identify()
        Result:
            dict : GET parameters
        """
        params = {}
        # Configuration
        params["host"] = self.domain
        params["cookie"] = user_properties.cookie
        if user_properties.ip_address is not None:
            params["ip"] = user_properties.ip_address
        if self.idle_timeout is not None:
            params["timeout"] = self.idle_timeout
        # Identification
        params["cv_email"] = user_properties.email
        for k, v in user_properties.user_properties.iteritems():
            params["cv_" + k] = v.encode('utf-8')
        return params

    def track_event(self, user_properties, event_name, event_data={}):
        """
        Tracks pageviews and custom events
        Parameters:
            user_properties - WoopraUser : returned by call to identify()
            event_name - str : The name of the event
            event_data - dict : Properties the custom event
                key - str : the event property name
                value - str, int, bool : the event property value
        Result:
            urllib2.Response : result of the API call
        Examples:
            # This code tracks a custom event through the back-end:
            woopra.track('signup', {'company' : 'My Business', 'username' : 'johndoe', 'plan' : 'Gold'})
        """
        params = self.get_params(user_properties)
        params["ce_name"] = event_name
        for k, v in event_data.iteritems():
            params["ce_" + k] = v.encode('utf-8')
        url = "/track/ce/?" + urllib.urlencode(params) + "&response=json&ce_app=" + WoopraTracker.SDK_ID
        return self._woopra_http_request(user_properties, url)

    def track_identify(self, user_properties):
        """
        Pushes the indentification information on the user to Woopra in case no tracking event occurs.
        Parameter:
            user_properties - WoopraUser : returned by call to identify()
        Result:
            urllib2.Response : result of the API call
        """
        params = self.get_params(user_properties)
        url = "/track/identify/?" + urllib.urlencode(params) + "&response=json&ce_app=" + WoopraTracker.SDK_ID
        return self._woopra_http_request(user_properties, url)

    def search_profile(self, user_properties):
        """
        Retrieves a detailed visitor profile.
        Parameter:
            user_properties - WoopraUser : returned by call to identify()
        Result:
            urllib2.Response : result of the API call
        """
        url = "/rest/2.2/profile"
        data = {'website': self.domain, 'email': user_properties.email}
        return self._woopra_http_request(user_properties, url, data)

    def _woopra_http_request(self, user_properties, url, data=None):
        """
        Sends an HTTP Request to Woopra
        Parameters:
            user_properties - WoopraUser : returned by call to identify()
            url - string : API url to call without http://www.woopra.com
            data - dict (optional) : POST data
        Result:
            urllib2.Response : result of the API call
        """
        if data:
            headers = {'User-agent': user_properties.user_agent, 'Authorization': 'Basic ' + self.access_key}
            req = urllib2.Request(self.BASE_URL + url, urllib.urlencode(data), headers)
        else:
            req = urllib2.Request(self.BASE_URL + url)
        resp = urllib2.urlopen(req)
        return resp

    def set_timeout(self, timeout):
        """
        Sets the Woopra request timeout.
        Parameter:
            timeout - the new timeout
        Result:
            None
        """
        self.idle_timeout = timeout
