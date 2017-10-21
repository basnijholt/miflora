from miflora.backends import AbstractBackend


class MockBackend(AbstractBackend):

    def __init__(self, adapter):
        super(self.__class__, self).__init__(adapter)

    def check_backend(self):
        pass
