import os

os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("SECRET_KEY", "django-insecure-test-only-key")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
os.environ.setdefault("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/candor_test")

from config.settings import *  # noqa: F403
