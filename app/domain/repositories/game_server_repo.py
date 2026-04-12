class GameServerRepository:

    def add(self, game_server):
        raise NotImplementedError

    def update(self, game_server):
        raise NotImplementedError

    def get(self, id):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def delete(self, id):
        raise NotImplementedError

