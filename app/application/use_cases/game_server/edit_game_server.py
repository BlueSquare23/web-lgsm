from app.domain.entities.game_server import GameServer

class EditGameServer:

    def __init__(self, game_server_repository):
        self.game_server_repository = game_server_repository

    def execute(self, id, install_name, install_path, script_name, username, install_type, install_host=None, install_finished=False, install_failed=False, keyfile_path=None):

        # TODO: Convert to **kwargs, for rn fine cause still dev and debugging.
        # But once cooled, use less verbose option.

        # Convert data to domain entity.
        game_server = GameServer(
            id = id,
            install_name = install_name,
            install_path = install_path,
            script_name = script_name,
            username = username,
            is_container = True if install_type == 'docker' else False,
            install_type = install_type,
            install_host = '127.0.0.1' if not install_host else install_host,
            install_finished = install_finished,
            install_failed = install_failed,
            keyfile_path = keyfile_path,
        )

        # TODO: Perhaps introduce try catch exception handling here. Need
        # specific exceptions for each layer to pass off to the next. But will
        # figure it out later.
        return self.game_server_repository.update(game_server)

