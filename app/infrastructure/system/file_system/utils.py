def is_utf8_decodable(file_path):
    try:
        with open(file_path, "rb") as f:
            # Read a sample chunk
            chunk = f.read(4096) 
            chunk.decode("utf-8")
            return True
    except UnicodeDecodeError:
        return False
