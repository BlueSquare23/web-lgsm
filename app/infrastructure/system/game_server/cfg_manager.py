import os
import getpass
import json

from flask import current_app, flash

from app.utils.paths import PATHS

from app.infrastructure.system.command_executor.command_executor import CommandExecutor
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.system.user.user_module_service import UserModuleService 


class CfgManager:
    USER = getpass.getuser()

    def __init__(self, executor=UserModuleService(), proc_info_service=InMemProcInfoRepository(), command_exec_service=CommandExecutor()):
        self.executor = executor
        self.proc_info_service = proc_info_service
        self.command_exec_service = command_exec_service

    def find_cfg_paths(self, server):
        cfg_whitelist = open("json/accepted_cfgs.json", "r")
        json_data = json.load(cfg_whitelist)
        cfg_whitelist.close()
        valid_gs_cfgs = json_data["accepted_cfgs"]

        if server.install_type == 'remote':
            return self.find_cfg_paths_ssh(server, valid_gs_cfgs)

        args = [ server.install_path, valid_gs_cfgs ]

        kwargs = dict()
        if server.username != CfgManager.USER:
            kwargs = { 'as_user': server.username }

        return self.executor.call('find_cfg_paths', *args, **kwargs)


    def find_cfg_paths_ssh(self, server, valid_gs_cfgs):
        cfg_paths = []
        wanted = []

        for cfg in valid_gs_cfgs:
            wanted += ["-name", cfg, "-o"]

        cmd = [
            PATHS["find"],
            server.install_path,
            "-name",
            "config-default",
            "-prune",
            "-type",
            "f",
        ] + wanted[:-1]

        cmd_id = "find_cfg_paths"
        success = self.command_exec_service().run_command(cmd, server, cmd_id)
        proc_info = self.proc_info_service.get_process(cmd_id)

        # If the ssh connection itself fails return False.
        if not success:
            current_app.logger.info(proc_info)
            flash("Problem connecting to remote host!", category="error")
            return cfg_paths

        if proc_info.exit_status > 0:
            return cfg_paths

        for item in proc_info.stdout:
            item = item.strip()
            current_app.logger.info(item)

            # Check str coming back is valid cfg name str.
            if os.path.basename(item) in valid_gs_cfgs:
                cfg_paths.append(item)

        return cfg_paths
