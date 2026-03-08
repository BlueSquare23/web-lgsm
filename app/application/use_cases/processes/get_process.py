class GetProcess:

    def __init__(self, process_repository):
        self.process_repository = process_repository

    def execute(self, server_id, create=False):
        return self.process_repository.get(server_id, create)

