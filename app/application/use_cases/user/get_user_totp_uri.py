class GetUserTotpUri:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, user_id):
        return self.user_repository.get_totp_uri(user_id)

