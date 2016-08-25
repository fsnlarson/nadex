"""
Connection Module
Handles HTTP operations
"""

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import logging
import requests

from .constants import TRADE_URL, IG_HEADERS
from .rest_exceptions import *

log = logging.getLogger("nadex.connection")


class Connection(object):
    """
    Connection class manages the connection to the Nadex REST API.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.timeout = 7.0  # need to catch timeout?

        # set up the session.  Session enables cookies, gzip, and keep-alive
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "IGNadexApp/5.0.5.1 CFNetwork/758.4.3 Darwin/15.5.0",
            'x-device-user-agent': "vendor=Minsk | applicationType=NADEX_PROMO | platform=iOS | deviceType=phone | version=5.0.5"
        }
        self._session.headers.update(**IG_HEADERS)

        self._last_response = None

    def set_xst(self, xst):
        self._session.headers['X-SECURITY-TOKEN'] = xst

    def full_path(self, url):
        return "{}/{}".format(self.base_url, url)

    def get_xst(self):
        return self._session.headers.get("X-SECURITY-TOKEN")

    def _run_method(self, method, url, data=None, query=None, headers=None):
        # make full path if not given
        if url and url[:4] != "http":
            if url[0] == '/':  # can call with /resource if you want
                url = url[1:]
            url = self.full_path(url)
        elif not url:  # blank path
            url = self.full_path(url)

        if query:
            qs = urlencode(query)
            if qs:
                qs = "?" + qs
            url += qs

        # mess with content
        log.debug("%s %s" % (method, url))

        # make and send the request
        if headers:
            self._session.headers.update(**headers)
        return self._session.request(method, url, json=data, timeout=self.timeout, verify=True)

    # CRUD methods
    def get(self, resource="", rid=None, **query):
        """
        Retrieves the resource with given id 'rid', or all resources of given type.
        """
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        response = self._run_method('GET', resource, query=query)
        return self._handle_response(resource, response)

    def update(self, resource, rid, updates):
        """
        Updates the resource with id 'rid' with the given updates dictionary.
        """
        if resource[-1] != '/':
            resource += '/'
        resource += str(rid)
        return self.put(resource, data=updates)

    def create(self, resource, data):
        """
        Create a resource with given data dictionary.
        """
        return self.post(resource, data)

    def delete(self, resource, rid=None):  # note that rid can't be 0 - problem?
        """
        Deletes the resource with given id 'rid', or all resources of given type if rid is not supplied.
        """
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        response = self._run_method('DELETE', resource)
        return self._handle_response(resource, response, suppress_empty=True)

    # Raw-er stuff

    def make_request(self, method, url, data=None, params={}, headers={}):
        response = self._run_method(method, url, data, params, headers)
        return self._handle_response(url, response)

    def put(self, url, data):
        """
        Make a PUT request to save data.
        data should be a dictionary.
        """
        response = self._run_method('PUT', url, data=data)
        log.debug("OUTPUT: %s" % response.content)
        return self._handle_response(url, response)

    def post(self, url, data):
        """
        POST request for creating new objects.
        data should be a dictionary.
        """
        response = self._run_method('POST', url, data=data)
        return self._handle_response(url, response)

    def _handle_response(self, url, res, suppress_empty=True):
        """
        Returns parsed JSON or raises an exception appropriately.
        """
        self._last_response = res
        result = {}
        if res.status_code in (200, 201, 202):
            try:
                result = res.json()
            except Exception as e:  # json might be invalid, or store might be down
                e.message += " (_handle_response failed to decode JSON: " + str(res.content) + ")"
                raise  # TODO better exception
        elif res.status_code == 204 and not suppress_empty:
            raise EmptyResponseWarning("%d %s @ %s: %s" % (res.status_code, res.reason, url, res.content), res)
        elif res.status_code >= 500:
            raise ServerException("%d %s @ %s: %s" % (res.status_code, res.reason, url, res.content), res)
        elif res.status_code >= 400:
            raise ClientRequestException("%d %s @ %s: %s" % (res.status_code, res.reason, url, res.content), res)
        elif res.status_code >= 300:
            raise RedirectionException("%d %s @ %s: %s" % (res.status_code, res.reason, url, res.content), res)

        # update security token
        xst = res.headers.get("X-SECURITY-TOKEN")
        if xst:
            self._session.headers.update({"X-SECURITY-TOKEN": xst})

        return result

    def __repr__(self):
        return "%s %s" % (self.__class__.__name__, self.base_url)
