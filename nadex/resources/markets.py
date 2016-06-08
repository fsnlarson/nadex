from .base import ApiResource, ListableApiResource, ListableApiSubResource


class Epic(ApiResource):
    resource_name = 'markets/details'

    #
    # if epic_ref.instrument and epic_ref.marketSnapshot:
    #     if not (epic_ref.instrument.instrumentType and
    #                 epic_ref.instrument.marketName and
    #                 epic_ref.instrument.displayPrompt):
    #         return
    #
    # return Contract(instrumentType=epic_ref.instrument.instrumentType,
    #                 epic=epic,
    #                 displayOffer=epic_ref.marketSnapshot.displayOffer,
    #                 displayBid=epic_ref.marketSnapshot.displayBid,
    #                 instrumentName=epic_ref.instrument.marketName,
    #                 displayPeriod=epic_ref.instrument.displayPrompt)


class Market(ListableApiResource):
    resource_name = 'markets/navigation'


class Instrument(ListableApiSubResource):
    resource_name = 'markets/navigation'


class Timeseries(ListableApiResource):
    resource_name = 'markets/navigation'


class Contract(ListableApiResource):
    resource_name = 'markets/navigation'

   # def __init__(self, displayOffer=None, displayBid=None, instrumentName=None, epic=None, instrumentType=None,
   #               displayPeriod=None, bestOffer=None, **kwargs):
   #      """
   #      @param bid: Retrieves the current highest bid for the contract (example: "30.00")
   #      @param contract: Retrieves the name of the contract (example: "GBP/USD >1.5120 (3PM)")
   #      @param epic: Retrieves the unique identifier for the contract as created by the exchange (example: "NB.D.OPT-GBP-USD.1-1-15Jan15")
   #      @param expirydate: Retrieves the date on which the contract will expire (example: "20-JAN-15")
   #      @param offer: Retrieves the current lowest offer for the contract (example: "20.50")
   #      @param type: Retrieves the type of contract: one of 'binary', 'spread', or 'event'
   #      """
   #      self._offer = displayOffer or 'NoOffer'
   #      self._bid = displayBid or 'NoBid'
   #      self._contract = instrumentName
   #      self._epic = epic
   #      self._instrument_type = instrumentType.lower()
   #      self._expirydate = displayPeriod
   #      self._best_offer = bestOffer
   #      self.__rest = kwargs
