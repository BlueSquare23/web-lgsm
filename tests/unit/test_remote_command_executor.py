import paramiko

## Ssh Test Classes
class FakeChannel:
    def __init__(self, stdout="", stderr="", exit_status=0):
        self._stdout = stdout.encode()
        self._stderr = stderr.encode()
        self.exit_status = exit_status

        self._stdout_read = False
        self._stderr_read = False

    def set_combine_stderr(self, val):
        pass

    def exec_command(self, cmd):
        self.cmd = cmd

    def settimeout(self, timeout):
        self.timeout = timeout

    def recv_ready(self):
        return not self._stdout_read and bool(self._stdout)

    def recv(self, n):
        self._stdout_read = True
        return self._stdout

    def recv_stderr_ready(self):
        return not self._stderr_read and bool(self._stderr)

    def recv_stderr(self, n):
        self._stderr_read = True
        return self._stderr

    def exit_status_ready(self):
        return (
            (self._stdout_read or not self._stdout) and
            (self._stderr_read or not self._stderr)
        )

    def recv_exit_status(self):
        return self.exit_status


class FakeTransport:
    def __init__(self, channel):
        self.channel = channel

    def open_session(self):
        return self.channel


class FakeSSHClient:
    def __init__(self, channel):
        self._transport = FakeTransport(channel)

    def get_transport(self):
        return self._transport


class FakeSSHClientInterface:
    def __init__(self, channel):
        self.channel = channel

    def get_client(self, username, hostname):
        return FakeSSHClient(self.channel)


class DummyConfig:
    def getboolean(self, *_):
        return False

def test_run_success_stdout():
    from app.infrastructure.system.command_executor.remote_command_executor import SshCommandExecutor
    from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

    channel = FakeChannel(stdout="hello\n", exit_status=0)
    client_interface = FakeSSHClientInterface(channel)

    executor = SshCommandExecutor(DummyConfig(), client_interface)

    class Server:
        install_host = "host"
        username = "user"
        id = "cmd1"

    result = executor.run(["echo", "hello"], server=Server())

    proc_info = InMemProcInfoRepository().get("cmd1")

    assert result is True
    assert "hello\n" in proc_info.stdout
    assert proc_info.exit_status == 0

def test_run_stderr_capture():
    from app.infrastructure.system.command_executor.remote_command_executor import SshCommandExecutor
    from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

    channel = FakeChannel(stderr="error occurred\n", exit_status=1)
    client_interface = FakeSSHClientInterface(channel)

    executor = SshCommandExecutor(DummyConfig(), client_interface)

    class Server:
        install_host = "host"
        username = "user"
        id = "cmd2"

    executor.run(["badcmd"], server=Server())

    proc_info = InMemProcInfoRepository().get("cmd2")

    assert "error occurred\n" in proc_info.stderr
    assert proc_info.exit_status == 1

def test_command_is_joined_correctly():
    from app.infrastructure.system.command_executor.remote_command_executor import SshCommandExecutor

    channel = FakeChannel(stdout="ok\n")
    client_interface = FakeSSHClientInterface(channel)

    executor = SshCommandExecutor(DummyConfig(), client_interface)

    class Server:
        install_host = "host"
        username = "user"
        id = "cmd3"

    executor.run(["echo", "hello world"], server=Server())

    assert channel.cmd == "echo 'hello world'"

class FailingClientInterface:
    def get_client(self, username, hostname):
        raise paramiko.SSHException("connection failed")


def test_ssh_exception_handling():
    from app.infrastructure.system.command_executor.remote_command_executor import SshCommandExecutor
    from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository

    executor = SshCommandExecutor(DummyConfig(), FailingClientInterface())

    class Server:
        install_host = "host"
        username = "user"
        id = "cmd4"

    result = executor.run(["ls"], server=Server())

    proc_info = InMemProcInfoRepository().get("cmd4")

    assert result is False
    assert proc_info.exit_status == 5
    assert any("connection failed" in e for e in proc_info.stderr)
