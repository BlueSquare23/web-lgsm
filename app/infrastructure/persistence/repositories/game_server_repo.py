import os
import json
import base64
import onetimepass

from app.domain.repositories.game_server_repo import GameServerRepository
from app.domain.entities.game_server import GameServer
from app.infrastructure.persistence.models.game_server_model import GameServerModel
from app import db

class SqlAlchemyGameServerRepository(GameServerRepository):

    def add(self, game_server):
        model = GameServerModel(
            id = game_server.id,
            install_name = game_server.install_name,
            install_path = game_server.install_path,
            script_name = game_server.script_name,
            username = game_server.username,
            is_container = game_server.is_container,
            install_type = game_server.install_type,
            install_host = game_server.install_host,
            install_finished = game_server.install_finished,
            install_failed = game_server.install_failed,
            keyfile_path = game_server.keyfile_path,
        )
        db.session.add(model)
        db.session.commit()
        return model.id


    def update(self, game_server):
        model = GameServerModel.query.filter_by(id=game_server.id).first()

        # If game_server doesn't exist, add them.
        if model == None:
            return self.add(game_server)

        for key, value in game_server.__dict__.items():
            setattr(model, key, value)

        db.session.commit()
        return True


    def get(self, game_server_id):
        """Convert game_server_id into GameServer entity"""
        model = GameServerModel.query.filter_by(id=game_server_id).first()

        if model == None:
            return None

        # Convert model object to Job entity.
        data = {
            'id': model.id,
            'install_name': model.install_name,
            'install_path': model.install_path,
            'script_name': model.script_name,
            'username': model.username,
            'is_container': model.is_container,
            'install_type': model.install_type,
            'install_host': model.install_host,
            'install_finished': model.install_finished,
            'install_failed': model.install_failed,
            'keyfile_path': model.keyfile_path,
        }
        game_server = GameServer(**data)

        return game_server


    def query(self, key, value):
        """Get GameServer entity by key value"""
        model = GameServerModel.query.filter_by(**{key: value}).first()

        if model == None:
            return None

        # Use existing get game_server to convert model id to domain GameServer entity.
        return self.get(model.id)


    def delete(self, game_server_id):
        model = GameServerModel.query.filter_by(id=game_server_id).first()

        if not model:
            return False

        db.session.delete(model)
        db.session.commit()
        return True


    def list(self):
        """
        Fetches list of all game_servers from DB and converts them to list of GameServer
        entity objects.
        """
        all_models = GameServerModel.query.all()
        all_game_servers = []

        for model in all_models:
            all_game_servers.append(self.get(model.id))
            
        return all_game_servers


