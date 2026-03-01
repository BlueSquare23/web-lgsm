class DeleteGameServer:

    def __init__(self, game_server_repository, game_server_manager):
        self.game_server_repository = game_server_repository
        self.game_server_manager = game_server_manager

    def execute(self, id, remove_files, delete_user):
        """
        Returns:
            Bool: True if successfully deleted, false otherwise.
        """
        server = self.game_server_repository.get(id)

        # Only remove from DB.
        if not remove_files:
            return self.game_server_repository.delete(id)

        # If system delete success, delete from DB.
        if self.game_server_manager.delete(server, delete_user):
            return self.game_server_repository.delete(id)

