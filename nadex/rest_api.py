import sys
from nadex import connection
from nadex.resources import *


class NadexRestApi(object):
    """
    """

    def __init__(self, conn=None):
        if not conn:
            conn = connection.Connection()
        self.connection = conn

    def __getattr__(self, item):
        return ApiResourceWrapper(item, self)


class ApiResourceWrapper(object):
    """
    Provides dot access to each of the API resources
    while proxying the connection parameter so that
    the user does not need to know it exists
    """

    def __init__(self, resource_class, api):
        """
        :param resource_class: String or Class to proxy
        :param api: API whose connection we want to use
        :return: A wrapper instance
        """
        if isinstance(resource_class, str):
            self.resource_class = self.str_to_class(resource_class)
        else:
            self.resource_class = resource_class

        self.connection = api.connection

    def __getattr__(self, item):
        """
        Proxies access to all methods on the resource class,
        injecting the connection parameter before any
        other arguments

        TODO: Distinguish between methods and attributes
        on the resource class?
        """
        return lambda *args, **kwargs: (getattr(self.resource_class, item))(*args, connection=self.connection, **kwargs)

    @classmethod
    def str_to_class(cls, str):
        """
        Transforms a string class name into a class object
        Assumes that the class is already loaded.
        """
        return getattr(sys.modules[__name__], str)
