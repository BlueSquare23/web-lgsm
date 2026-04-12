class ToUser:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, model):
        return self.user_repository.to_domain(model)

