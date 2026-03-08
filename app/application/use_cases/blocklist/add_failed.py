class AddFailedBlocklist:

    def __init__(self, blocklist_repository):
        self.blocklist_repository = blocklist_repository

    def execute(self, ip):
        return self.blocklist_repository.add(ip)

