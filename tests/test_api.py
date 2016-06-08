import unittest
from unittest.mock import MagicMock

from nadex.api import NadexRestApi


class TestNadex(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost"
        self.username = 'testuser'
        self.password = 'testpass'
        self.api = NadexRestApi()
        self.api.connection = MagicMock()

    def test_login(self):
        account = self.api.Account.login()
        self.api.connection.assert_called_with(3, 4, 5, key='value')

    '''
    def test_get_market_id(self):
        name = 'name'
        market_list_ref = []
        accept_match = None
        market_id = self.api._get_market_id(name, market_list_ref, accept_match)
        assert market_id

    def test_is_valid_direction(self, direction):
        pass

    def test_is_valid_price(self, price, type):
        pass

    def test_is_valid_size(self, size):
        pass

    def test_post(self, url, post_content):
        pass

    def test_authenticated(self):
        pass

    def test_balance(self):
        pass

    def test_cancel_all_orders(self):
        pass

    def test_cancel_order(self, id):
        pass

    def test_create_order(self, price, direction, epic, size):
        pass

    def test_get_contract(self, epic):
        pass

    def test_get_contracts(self, market, instrument, series):
        pass

    def test_get_epic(self, period, market, time, instrument, strike):
        pass

    def test_get_market_instruments(self, name):
        pass

    def test_get_markets(self):
        pass

    def test_get_quote(self, instrument):
        pass

    def test_get_time_series(self, market, instrument):
        pass

    def test_login(self):
        pass

    def test_retrieve_order(self, order_id):
        pass

    def test_retrieve_orders(self):
        pass

    def test_retrieve_position(self, position_id):
        pass

    def test_retrieve_positions(self):
        pass
    '''
