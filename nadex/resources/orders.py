from .base import *


class Order(ListableApiResource, CreatableApiResource):
    resource_name = 'orders/workingorders'

    @classmethod
    def _create_path(cls):
        return 'dma/workingorders'
