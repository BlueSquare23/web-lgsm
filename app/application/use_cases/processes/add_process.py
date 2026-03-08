class AddProcess:

    def __init__(self, process_repository):
        self.process_repository = process_repository

    def execute(self, server_id, proc_info):
        return self.process_repository.add(server_id, proc_info)

