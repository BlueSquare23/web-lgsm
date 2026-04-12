class Audit:
    """
    Domain entity for audit logger.
    """
    def __init__(self, id, user_id, username, message, date_created):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.message = message
        self.date_created = date_created
