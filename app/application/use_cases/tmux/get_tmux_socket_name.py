class GetTmuxSocketName:

    def __init__(self, tmux_socket_cache_handler):
        tmux_socket_cache_handler=tmux_socket_cache_handler

    def execute(self, server):
        return self.tmux_socket_cache_handler.get_tmux_socket_name(server)
