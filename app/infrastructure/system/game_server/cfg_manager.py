import os
import getpass
import json
import logging

from app.utils.paths import PATHS
from app.infrastructure.system.command_executor.command_executor import CommandExecutor
from app.infrastructure.system.repositories.proc_info_repo import InMemProcInfoRepository
from app.infrastructure.system.user.user_module_service import UserModuleService 


class CfgManager:
    USER = getpass.getuser()

    def __init__(self, executor=UserModuleService(), proc_info_repo=InMemProcInfoRepository(), command_executor=CommandExecutor(), logger=logging.getLogger(__name__)):
        self.executor = executor
        self.proc_info_repo = proc_info_repo
        self.command_executor = command_executor
        self.logger = logger

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
        success = self.command_executor.run(cmd, server, cmd_id)
        proc_info = self.proc_info_repo.get(cmd_id)

        # If the ssh connection itself fails return False.
        if not success:
            self.logger.info(proc_info)
# Convert to exception
#            flash("Problem connecting to remote host!", category="error")
            return cfg_paths

        if proc_info.exit_status > 0:
            return cfg_paths

        for item in proc_info.stdout:
            item = item.strip()
            self.logger.info(item)

            # Check str coming back is valid cfg name str.
            if os.path.basename(item) in valid_gs_cfgs:
                cfg_paths.append(item)

        return cfg_paths
