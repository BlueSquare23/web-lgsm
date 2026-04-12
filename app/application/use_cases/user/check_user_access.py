class CheckUserAccess:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, user_id, route, server_id=None):
        return self.user_repository.has_access(user_id, route, server_id)

