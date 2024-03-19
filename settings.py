# configs, settings for project
from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://edu_user:edu_pass@0.0.0.0:5432/edu_db",
)
