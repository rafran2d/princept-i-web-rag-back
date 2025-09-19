from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv
import os
# Load the .env file
load_dotenv()

# Import your SQLAlchemy Base
from App.database import Base  # adjust according to your project
from App.Models.ChatMessageModel import ChatMessageModel
from App.Models.ChatModel import ChatModel
from App.Models.DocumentModel import DocumentModel
from App.Models.DocumentChunkModel import DocumentChunkModel
from App.Models.EmbedingModel import EmbeddingModel
from App.Models.UserModel import UserModel


# Create the SQLAlchemy URL from environment variables
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

database_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

# Get the Alembic config object
config = context.config

# Inject the URL into Alembic (overrides the URL in alembic.ini)
config.set_main_option("sqlalchemy.url", database_url)

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate' support
target_metadata = Base.metadata

# --- Offline migrations ---
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# --- Online migrations ---
def run_migrations_online() -> None:
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Execute the migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
