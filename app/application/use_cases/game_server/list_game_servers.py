class ListGameServers:

    def __init__(self, game_server_repository):
        self.game_server_repository = game_server_repository

    def execute(self):
        return self.game_server_repository.list()

