class VerifyUserTotp:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, user_id, token):
        return self.user_repository.verify_totp(user_id, token)

