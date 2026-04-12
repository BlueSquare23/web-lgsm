from app.domain.entities.user import User

class EditUser:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, id, username, password, role, permissions, otp_secret, otp_enabled, otp_setup):

        # TODO: Convert to **kwargs, for rn fine cause still dev and debugging.
        # But once cooled, use less verbose option.

        # Convert data to domain entity.
        user = User(
            id = id,
            username = username,
            password =password,
            role = role,
            permissions = permissions, 
            otp_secret = otp_secret, 
            otp_enabled = otp_enabled,
            otp_setup = otp_setup
        )

        # TODO: Perhaps introduce try catch exception handling here. Need
        # specific exceptions for each layer to pass off to the next. But will
        # figure it out later.
        return self.user_repository.update(user)

