class GetGameServer:

    def __init__(self, game_server_repository):
        self.game_server_repository = game_server_repository

    def execute(self, game_server_id):
        return self.game_server_repository.get(game_server_id)

