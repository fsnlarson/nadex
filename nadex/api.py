from nadex.rest_api import NadexRestApi
from nadex.stream_api import NadexStreamApi
from .connection import Connection
from .constants import TRADE_URL

class NadexApi(object):

    def __init__(self, username=None, password=None, base_url=TRADE_URL):
        self.username = username
        self.password = password

        conn = Connection(base_url)

        self.rest_api = NadexRestApi(conn)
        self.stream_api = None
        self.account = None
        self._markets = {}
        self._contracts = {}

    def update_markets(self):
        # get list of markets
        markets = client.Market.all()
        for m in markets:
            print(m.id, m.name)
            self._markets[m.id] = {}
            # get details of the market. e.g. Commodity market has Oil, Corn, etc.
            detail = client.Market.get(m.id)
            for d in detail:
                self._markets[m.id][d.id] = d.name
                print("  ", d.id, d.name)

    def login(self):
        # raise error if login fails
        self.account = self.rest_api.Account.login(self.username, self.password)
        # Establishing a new connection to Lightstreamer Server
        print("Starting connection: {}".format(self.account.lightstreamerEndpoint))
        self.stream_api = NadexStreamApi(self.account, self.rest_api)

        try:
            self.stream_api.connect()
        except Exception as e:
            print("Unable to connect to Lightstreamer Server")
            print(traceback.format_exc())
        return
