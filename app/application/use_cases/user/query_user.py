class QueryUser:
    """
    Like GetUser, but query by key and value.
    """

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, key, value):
        return self.user_repository.query(key, value)

