class NadexError(Exception):
    pass

class NadexAuthError(NadexError):
    message = ("You must set NADEXUSERNAME and NADEXPASSWORD"
               "in your environment with your Nadex username and password")

class NadexMarketListRetrieveError(NadexError):
    message = "failed to retrieve the market list from the exchange: market_id={}"


class NadexOrderRetrieveError(NadexError):
    message = "failed to retrieve the order list from the exchange"


class NadexPositionRetrieveError(NadexError):
    message = "failed to retrieve the position list from the exchange"


class NadexQuoteRetrieveError(NadexError):
    message = "failed to retrieve the quote from the exchange"


class NadexEpicRetrieveError(NadexError):
    message = "failed to retrieve the epic: epic={epic}"


# "ERROR: get_epic(): failed to retrieve the market list from the exchange for market market_id\n"
# "ERROR: get_epic(): invalid period must be one of: daily
# "ERROR: get_market_instruments(): failed to retrieve the market list from the exchange for market market_id\n"
# "ERROR: get_market_instruments(): failed to retrieve the market list from the exchange\n"
# "ERROR: get_markets(): failed to retrieve the market list from the exchange\n"
# "ERROR: get_quote(): failed to retrieve the market list from the exchange for epic epic\n"
# "ERROR: get_time_series(): failed to retrieve the market list from the exchange for market instrument_id\n"
# "ERROR: get_time_series(): failed to retrieve the market list from the exchange for market market_id\n"
# "ERROR: get_time_series(): failed to retrieve the market list from the exchange\n"
