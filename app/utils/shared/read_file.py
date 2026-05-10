import os
import gzip
import base64
import mimetypes

def read_file(file_path):
    """
    Shared file read module. Reads files and returns base64 encoded contents.
    Only processes plain text files.

    Returns:
        dict with keys: status, mime_type, data
    """
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            return {
                "status": "not_found", 
                "mime_type": None,
                "data": None
            }

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
                return {
                    "status": "unsupported_type",
                    "mime_type": mime_type,
                    "data": None
                }

        # Read the file's content as bytes.
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        # Gzip compress
        compressed_bytes = gzip.compress(file_bytes)

        # Base64 encode compressed bytes
        encoded_string = base64.b64encode(compressed_bytes).decode('utf-8')

        return {
            "status": "success",
            "mime_type": mime_type or "text/plain",
            "data": encoded_string
        }

    except Exception:
        return {
            "status": "error",
            "mime_type": None,
            "data": None
        }
    
