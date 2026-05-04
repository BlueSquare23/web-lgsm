import os

class FilenameLength:

    def execute(self, value, max_length=100):
        if not value:
            return False, "Invalid filename"

        filename = os.path.basename(value)

        if len(filename) > max_length:
            return False, f"Filename must be at most {max_length} characters long"

        return True, None

