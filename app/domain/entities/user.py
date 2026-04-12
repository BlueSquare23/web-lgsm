class User:
    """
    Abstract domain layer representation of a User.
    """
    def __init__(self, id, username, password, role, permissions, otp_secret, otp_enabled, otp_setup):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.permissions = permissions
        self.otp_secret = otp_secret
        self.otp_enabled = otp_enabled
        self.otp_setup = otp_setup



