class QueryGameServer:
    """
    Like GetGameServer, but query by key and value.
    """

    def __init__(self, game_server_repository):
        self.game_server_repository = game_server_repository

    def execute(self, **kwargs):
        return self.game_server_repository.query(**kwargs)

