import os
import base64
import mimetypes

def read_file(file_path):
    """
    Shared file read module. Reads files and returns base64 encoded contents.
    Only processes plain text files.
    """
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            return None

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_path)

        # If MIME type clearly indicates non-text, reject
        if mime_type is not None:
            if not mime_type.startswith('text/') and mime_type not in [
                'application/json', 
                'application/xml',
                'application/javascript',
                'application/x-yaml'
            ]:
                return None

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
    
