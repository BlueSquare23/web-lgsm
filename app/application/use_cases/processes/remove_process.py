class RemoveProcess:

    def __init__(self, process_repository):
        self.process_repository = process_repository

    def execute(self, server_id):
        return self.process_repository.remove(server_id)

