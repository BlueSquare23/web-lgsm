import os
import base64

def read_file(file_path):
    """
    Shared file read module. Reads files and returns base64 encoded contents.
    """
    try:
        # Read the file's content as bytes.
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

            # Encode the bytes into Base64 bytes
            encoded_bytes = base64.b64encode(file_bytes)

            # Decode the Base64 bytes to a standard string
            encoded_string = encoded_bytes.decode('utf-8')
            return encoded_string

    except Exception:
        return None
    
