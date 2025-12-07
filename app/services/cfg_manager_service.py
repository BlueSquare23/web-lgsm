import getpass
import json
from .user_module_service import UserModuleService
from .command_exec_service.command_exec_service import CommandExecService

class CfgManagerService:
    USER = getpass.getuser()

    def __init__(self, modules_dir=None):
        self.modules_dir = modules_dir
        self.executor = UserModuleService(self.modules_dir)


    def find_cfg_paths(self, server):
        cfg_whitelist = open("json/accepted_cfgs.json", "r")
        json_data = json.load(cfg_whitelist)
        cfg_whitelist.close()
        valid_gs_cfgs = json_data["accepted_cfgs"]

        if server.install_type == 'remote':
            return self.find_cfg_paths_ssh(valid_gs_cfgs)

        args = [ server.install_path, valid_gs_cfgs ]

        kwargs = dict()
        if server.username != CfgManagerService.USER:
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
   
        success = CommandExecService(ConfigManager()).run_command(cmd, server, cmd_id)
        proc_info = ProcInfoService().get_process(cmd_id)

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
