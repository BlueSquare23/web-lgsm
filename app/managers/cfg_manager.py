import os
import getpass
import json

from flask import current_app, flash

from app.utils.paths import PATHS
from app.config import ConfigManager

#from app.services import UserModuleService, ProcInfoService, CommandExecService

class CfgManager:
    USER = getpass.getuser()

# This is a dirty hack just injecting these dependencies. We need to have
# better architectural separation between managers and services. But till
# ProcInfo / CommandExec stuff is re-arched, this'll have to do.
    def __init__(self, executor, proc_info_service, command_exec_service):
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
        success = self.command_exec_service(ConfigManager()).run_command(cmd, server, cmd_id)
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
