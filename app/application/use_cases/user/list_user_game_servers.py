import json

class ListUserGameServers:

    def __init__(self, user_repository, game_server_repository):
        self.user_repository = user_repository
        self.game_server_repository = game_server_repository

    def execute(self, user_id):
        user = self.user_repository.get(user_id)
        
        if user.role == 'admin':
            return self.game_server_repository.list()

        user_perms = json.loads(user.permissions)

        servers = []
        for server_id in user_perms['server_ids']:
            server = self.game_server_repository.get(server_id)
            servers.append(server)
        
        return servers

