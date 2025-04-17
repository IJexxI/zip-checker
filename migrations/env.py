from alembic import context
from sqlalchemy import create_engine
from app.storage.database import Base

config = context.config
connectable = create_engine(config.get_main_option("sqlalchemy.url"))

def run_migrations_online():
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    raise Exception("Offline mode not supported")
run_migrations_online()