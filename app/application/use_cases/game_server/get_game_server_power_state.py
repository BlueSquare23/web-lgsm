class GetGameServerPowerState:

    def __init__(self, game_server_manager):
        self.game_server_manager = game_server_manager

    def execute(self, game_server):
        return self.game_server_manager.get_power_state(game_server)

