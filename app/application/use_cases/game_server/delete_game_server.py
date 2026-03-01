class DeleteGameServer:

    def __init__(self, game_server_repository):
        self.game_server_repository = game_server_repository

    def execute(self, id):
        """
        Returns:
            Bool: True if successfully deleted, false otherwise.
        """
        return self.game_server_repository.delete(id)

