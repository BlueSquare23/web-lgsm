from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache

# Naming conventions for Flask-Migrate.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

# Initialize extensions
db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()
migrate = Migrate()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
