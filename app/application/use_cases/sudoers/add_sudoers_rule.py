class AddSudoersRule:

    def __init__(self, sudoers_service):
        self.sudoers_service = sudoers_service 

    def execute(self, username):
        return self.sudoers_service.add_user(username)

