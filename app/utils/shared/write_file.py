import os
import base64

def write_file(file_path, encoded_content):
    """
    Share module write file function. Decodes base64 to raw bytes, and writes
    to file_path.

    Returns:
        bool: True if write successful, False otherwise.
    """
    try:
        # Decode base64 to raw bytes
        content = base64.b64decode(encoded_content)

        with open(file_path, "wb") as f:
            f.write(content)

        return True

    except Exception:
        return False

