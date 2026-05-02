from ..base import *

class ValidCronExpr:
    def __init__(self, message="Invalid cron schedule!"):
        self.message = message

    def __call__(self, form, field):
        try:
            Cron(field.data)
        except ValueError:
            raise ValidationError(self.message)
