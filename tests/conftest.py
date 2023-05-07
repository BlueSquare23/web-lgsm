import os
import sys
import time
import shutil
import pytest
from pathlib import Path
from app import main
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app_path = os.path.abspath('../app')

sys.path.insert(0, app_path)

# Setup testing env.
def setup():
    try:
        # Move any current db files to epoch time .bak.
        db_file = 'app/database.db'
        if os.path.exists(db_file):
            epoch = str(int(time.time()))
            os.rename(db_file, db_file + '.' + epoch + '.bak')

#        # Create dummy Minecraft install for testing.
#        cfg_dst = os.path.abspath('./tests/test_data/Minecraft/lgsm/config-lgsm/mcserver/')
#        mc_dir = 'tests/test_data/Minecraft'
#        if not os.path.isdir(mc_dir):
#            os.makedirs(cfg_dst)
#
#        os.chdir(mc_dir)
#        os.system('wget -O linuxgsm.sh https://linuxgsm.sh')
#        os.chmod('linuxgsm.sh', 0o755)
#        os.system('./linuxgsm.sh mcserver')
#        os.chdir('../../..')
#        shutil.copy(os.path.abspath('./tests/test_data/common.cfg'), cfg_dst)
    except Exception as e:
        error = str(e)
        sys.exit(f"Setup function failed!!!\n{error}")

# Just run the setup once.
setup()

@pytest.fixture
def app():
    application = main()
    application.config.update({
        "TESTING": True,
    })

    yield application

@pytest.fixture
def client(app):
    return app.test_client()
