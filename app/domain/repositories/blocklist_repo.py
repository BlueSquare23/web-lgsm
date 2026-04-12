class BlocklistRepository:

    def add(self, ip):
        raise NotImplementedError

    def check(self, ip):
        raise NotImplementedError

