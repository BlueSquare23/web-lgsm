import pwd

class UserInfo():

    def get_uid(username):
        """
        Translates a username to a uid using pwd module.
    
        Args:
            username(str): User to get uid for
    
        Returns:
            uid (str): Either returns the uid for user or None if can't get uid
        """
        try:
            user_info = pwd.getpwnam(username)
            return user_info.pw_uid
        except KeyError:
            return None

