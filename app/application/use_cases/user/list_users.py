class ListUsers:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self):
        return self.user_repository.list()

