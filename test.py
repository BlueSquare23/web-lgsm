from app import create_app
from app.services import UserModuleExecService

app = create_app()

executor = UserModuleExecService('/home/blue/Projects/web-lgsm/app/utils/')

result1 = executor.call('find_cfg_paths', '/home/blue/Projects/web-lgsm/GameServers/Minecraft/', ['common.cfg'])

print(result1)

result2 = executor.call('find_cfg_paths', '/home/bf1942server/GameServers/Battlefield_1942/', ['common.cfg'], as_user='bf1942server')
print(result2)
