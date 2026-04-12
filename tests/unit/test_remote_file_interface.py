class FakeFile:
    def __init__(self, content=b"", should_fail=False):
        self.content = content
        self.should_fail = should_fail
        self.written = b""

    def read(self):
        if self.should_fail:
            raise Exception("read failed")
        return self.content

    def write(self, data):
        if self.should_fail:
            raise Exception("write failed")
        self.written += data.encode() if isinstance(data, str) else data

    def __enter__(self):
        if self.should_fail:
            raise Exception("file open failed")
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


class FakeSFTP:
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def open(self, path, mode):
        return self.file_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


class FakeSSHClient:
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def open_sftp(self):
        return FakeSFTP(self.file_obj)


class FakeSSHClientInterface:
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def get_client(self, username, hostname):
        return FakeSSHClient(self.file_obj)

def test_read_success():
    from app.infrastructure.system.file_system.remote_file_interface import SSHFileInterface

    fake_file = FakeFile(content=b"hello world")
    client_interface = FakeSSHClientInterface(fake_file)

    class Server:
        install_host = "host"
        username = "user"

    fs = SSHFileInterface(Server(), client_interface)

    result = fs.read("/fake/path")

    assert result == "hello world"

def test_read_failure_returns_none():
    from app.infrastructure.system.file_system.remote_file_interface import SSHFileInterface

    fake_file = FakeFile(should_fail=True)
    client_interface = FakeSSHClientInterface(fake_file)

    class Server:
        install_host = "host"
        username = "user"

    fs = SSHFileInterface(Server(), client_interface)

    result = fs.read("/fake/path")

    assert result is None

def test_write_success():
    from app.infrastructure.system.file_system.remote_file_interface import SSHFileInterface

    fake_file = FakeFile()
    client_interface = FakeSSHClientInterface(fake_file)

    class Server:
        install_host = "host"
        username = "user"

    fs = SSHFileInterface(Server(), client_interface)

    result = fs.write("/fake/path", "hello\r\nworld")

    assert result is True
    assert fake_file.written == b"hello\nworld"

def test_write_failure_returns_false():
    from app.infrastructure.system.file_system.remote_file_interface import SSHFileInterface

    fake_file = FakeFile(should_fail=True)
    client_interface = FakeSSHClientInterface(fake_file)

    class Server:
        install_host = "host"
        username = "user"

    fs = SSHFileInterface(Server(), client_interface)

    result = fs.write("/fake/path", "data")

    assert result is False

class TrackingSFTP(FakeSFTP):
    def __init__(self, file_obj):
        super().__init__(file_obj)
        self.last_path = None
        self.last_mode = None

    def open(self, path, mode):
        self.last_path = path
        self.last_mode = mode
        return self.file_obj


def test_write_uses_correct_mode():
    from app.infrastructure.system.file_system.remote_file_interface import SSHFileInterface

    fake_file = FakeFile()
    sftp = TrackingSFTP(fake_file)

    class Client:
        def open_sftp(self):
            return sftp

    class ClientInterface:
        def get_client(self, *_):
            return Client()

    class Server:
        install_host = "host"
        username = "user"

    fs = SSHFileInterface(Server(), ClientInterface())

    fs.write("/tmp/test.txt", "data")

    assert sftp.last_path == "/tmp/test.txt"
    assert sftp.last_mode == "w"
