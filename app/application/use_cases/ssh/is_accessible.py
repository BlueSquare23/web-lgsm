class IsAccessible:

    def __init__(self, port_checker):
        self.port_checker = port_checker

    def execute(self, hostname, port=22):
        return self.port_checker.check(hostname, port)

