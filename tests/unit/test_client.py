class FakeParamikoClient:
    def __init__(self):
        self.connected = False
        self.exec_called = False

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, hostname, username, key_filename, timeout,
                look_for_keys, allow_agent):
        self.connected = True
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename

    def exec_command(self, cmd, timeout=None):
        self.exec_called = True
        return None

    def close(self):
        self.closed = True

def test_get_client_success(monkeypatch):
    from app.infrastructure.system.ssh.client import SSHClientInterface

    fake_client = FakeParamikoClient()

    monkeypatch.setattr(
        "paramiko.SSHClient",
        lambda: fake_client
    )

    interface = SSHClientInterface()

    client = interface.get_client("user", "host")

    assert client is fake_client
    assert fake_client.connected is True
    assert fake_client.exec_called is True

def test_get_client_is_cached(monkeypatch):
    from app.infrastructure.system.ssh.client import SSHClientInterface

    created_clients = []

    def factory():
        c = FakeParamikoClient()
        created_clients.append(c)
        return c

    monkeypatch.setattr("paramiko.SSHClient", factory)

    interface = SSHClientInterface()

    c1 = interface.get_client("user", "host")
    c2 = interface.get_client("user", "host")

    assert c1 is c2
    assert len(created_clients) == 1

def test_healthcheck_failure_closes_client(monkeypatch):
    from app.infrastructure.system.ssh.client import SSHClientInterface
    import pytest

    class FailingClient(FakeParamikoClient):
        def exec_command(self, *args, **kwargs):
            raise Exception("boom")

    client = FailingClient()

    monkeypatch.setattr("paramiko.SSHClient", lambda: client)

    interface = SSHClientInterface()

    with pytest.raises(Exception):
        interface.get_client("user", "host")

    assert hasattr(client, "closed")

def test_get_ssh_key_file_exists(tmp_path, monkeypatch):
    from app.infrastructure.system.ssh.client import SSHClientInterface

    ssh_dir = tmp_path / ".ssh"
    ssh_dir.mkdir()

    key_name = "id_ecdsa_user_host"
    (ssh_dir / f"{key_name}.pub").write_text("pubkey")
    (ssh_dir / key_name).write_text("privatekey")

    monkeypatch.setattr("os.path.expanduser", lambda _: str(tmp_path))

    interface = SSHClientInterface()

    result = interface._get_ssh_key_file("user", "host")

    assert result.endswith(key_name)

def test_get_ssh_key_file_missing(tmp_path, monkeypatch):
    from app.infrastructure.system.ssh.client import SSHClientInterface

    ssh_dir = tmp_path / ".ssh"
    ssh_dir.mkdir()

    monkeypatch.setattr("os.path.expanduser", lambda _: str(tmp_path))

    interface = SSHClientInterface()

    result = interface._get_ssh_key_file("user", "host")

    assert result is None
