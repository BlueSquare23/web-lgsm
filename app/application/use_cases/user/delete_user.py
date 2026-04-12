class DeleteUser:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, id):
        """
        Returns:
            Bool: True if successfully deleted, false otherwise.
        """
        return self.user_repository.delete(id)

