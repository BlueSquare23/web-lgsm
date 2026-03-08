class ListProcesses:

    def __init__(self, process_repository):
        self.process_repository = process_repository

    def execute(self):
        return self.process_repository.list()

