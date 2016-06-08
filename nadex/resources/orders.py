import re
import time

from nadex.exceptions import NadexError
from .base import *
from .markets import Contract


class Order(ListableApiResource, CreatableApiResource):
    resource_name = 'orders/workingorders'

    # @classmethod
    # def listing(cls, showAll=False, connection=None):
    #    return cls.get(id='listing', showAll=str(showAll).lower(), connection=connection)

    @classmethod
    def create(cls, connection=None, params=None):
        response = cls._make_request('POST', cls._create_path(), connection, data=params.to_dict())
        return cls._create_object(response, connection=connection)

    @classmethod
    def create(cls, connection=None, order=None):
        order_time = int(time.time())
        direction = order.direction

        order.validate()
        contract = Contract.get(connection, epic=order.epic)

        # the market accepts only + or - for the direction this enables the aliases 'buy' and 'sell'
        if direction == 'buy':
            direction = '+'
        if direction == 'sell':
            direction = '-'

        # the price is dollars and cents for binaries and some instrument level
        # for spreads only format the price to a currency if the order type is 'binary'
        if contract.type == 'binary':
            price = "{:#2}".format(order.price)

        order_content = {
            "direction": direction,
            "epic": order.epic,
            "limitLevel": None,
            "lsServerName": connection.ls_server_url,
            "orderLevel": order.price,
            "orderSize": order.size,
            "orderType": "Limit",
            "sizeForPandLCalculation": order.size,
            "stopLevel": None,
            "timeInForce": "GoodTillCancelled",
            "timeStamp": order_time
        }
        o = super(Order, cls).create(connection=connection, order_content=order_content)
        if o:
            return o.json()['dealReference']

    # ---------------------------------------------------------------
    def is_valid_price(self, contract):
        if self._price not in ('-', '+'):
            return False

        if type == 'binary':
            if re.match(r"^(\d+\.\d{1,2}|\.\d{1,2}|\d+)", self._price):
                return True

            m = re.match(r'\.(\d+)', self._price)
            if m:
                # price 0, 25, 50, 75
                if not m.groups()[1] in (0, 25, 50, 75):
                    return False
        if contract.type == 'spread':
            if not re.match(r'^(\d+|\d+\.\d{1,4})', self._price):
                return False
        return True

    def is_valid_direction(self):
        valid = ('-', '+', 'buy', 'sell')
        return self._direction in valid

    def is_valid_size(self):
        try:
            int(self._size)
            return True
        except ValueError:
            return False

    def validate(self):
        contract = Contract.get(connection, epic=self.epic)

        if not self.is_valid_price(contract):
            raise NadexError("price {} is not valid".format(self.price))
        if not self.is_valid_direction():
            raise NadexError("direction {} is not valid".format(self.direction))
        if not contract:
            raise NadexError("epic {} is not valid".format(contract))
        if not self.is_valid_size():
            raise NadexError("size {} is not valid".format(self.size))

            # def __init__(self, market, workingOrder, instrument, marketSnapshot):
            #     if market and workingOrder:
            #         self._direction = workingOrder.direction
            #         self._price = workingOrder.level
            #         self._id = workingOrder.dealId
            #         self._epic = workingOrder.epic
            #         self._contract = market.instrumentName
            #         self._bid = market.displayBid or 'NoBid'
            #         self._offer = market.displayOffer or 'NoOffer'
            #         self._size = workingOrder.size
            #
            #     elif workingOrder and instrument and marketSnapshot:
            #         self._direction = workingOrder.direction
            #         self._price = workingOrder.triggerLevel
            #         self._id = workingOrder.id
            #         self._epic = instrument.epic
            #         self._contract = instrument.marketName
            #         self._bid = marketSnapshot.displayBid or 'NoBid'
            #         self._offer = marketSnapshot.displayOffer or 'NoOffer'
            #         self._size = workingOrder.size
