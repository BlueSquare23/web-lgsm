class GetUID:

    def __init__(self, system_user_info):
        self.system_user_info = system_user_info

    def execute(self, username):
        return self.system_user_info.get_uid(username)

