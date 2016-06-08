import os

from nadex.exceptions import NadexAuthError
from .base import CreatableApiResource


class Account(CreatableApiResource):
    resource_name = 'v2/security/authenticate'

    @classmethod
    def login(cls, connection=None, **params):
        username = params.get('username') or os.getenv('NADEXUSERNAME')
        password = params.get('password') or os.getenv('NADEXPASSWORD')

        if not (username and password):
            raise NadexAuthError

        params['username'] = username
        params['password'] = password

        return cls.create(connection=connection, **params)
