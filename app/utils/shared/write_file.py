import os
import base64

def write_file(file_path, encoded_content):
    """
    Share module write file function. Decodes base64 encoded string, and writes
    to file_path.

    Returns:
        bool: True if write successful, False otherwise.
    """
    try:
        # Decode base64 content str.
        content = base64.b64decode(encoded_content).decode('utf-8')

        with open(file_path, "w") as f:
            f.write(content.replace("\r", ""))

        return True

    except Exception as e:
        return False

