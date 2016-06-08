from .base import *


class TransferFrequency:
    LOAD_NOW = 'LOAD_NOW'
    LOAD_ONCE = 'LOAD_ONCE'
    LOAD_WEEKLY = 'LOAD_WEEKLY'
    LOAD_BIWEEKLY = 'LOAD_BIWEEKLY'
    LOAD_ON_DAY_1_AND_16 = 'LOAD_ON_DAY_1_AND_16'
    LOAD_MONTHLY = 'LOAD_MONTHLY'


class Summary(ApiSubResource):
    parent_resource = 'accounts'
    resource_name = 'summary'


class AvailableCash(ApiSubResource):
    parent_resource = 'accounts'
    resource_name = 'availablecash'


class Funds(CreateableApiSubResource):
    parent_resource = 'accounts'
    resource_name = 'funds'

    @classmethod
    def add(cls, parentid, amount, transferFrequency, startDate=None, endDate=None, connection=None):

        if amount <= 0:
            raise ValueError("amount must be positive")

        if transferFrequency == TransferFrequency.LOAD_ONCE and not startDate:
            raise ValueError("startDate is required for recurring transfers and LOAD_ONCE frequencies")
        params = dict(amount=amount, transferFrequency=transferFrequency)

        if startDate:
            params['startDate'] = startDate

        if endDate:
            params['endDate'] = endDate

        cls.create(parentid, id='add', connection=connection, **params)

    @classmethod
    def pending(cls, parentid, connection=None):
        cls.get(parentid, id='pending', connection=connection)

    @classmethod
    def cancel(cls, parentid, transferIds=None, connection=None):
        assert type(transferIds) in (list, tuple), "transferIds must be a list or tuple"
        for transferId in transferIds:
            assert type(transferId) == int, "transfer id must be integer"

        params = dict(transferIds=transferIds)

        cls.create(parentid, id='cancel', connection=connection, **params)


class Notes(ListableApiSubResource):
    resource_name = 'notes'
    parent_resource = 'accounts'


class DetailedNotes(ListableApiSubResource):
    resource_name = 'detailednotes'
    parent_resource = 'accounts'


class Portfolios(ListableApiSubResource, CreateableApiSubResource):
    resource_name = 'portfolios'
    parent_resource = 'accounts'


class Orders(ListableApiSubResource, CreateableApiSubResource):
    resource_name = 'orders'
    parent_resource = 'accounts'
