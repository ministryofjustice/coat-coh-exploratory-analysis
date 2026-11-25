import os


APP_ENV = os.getenv("APP_ENV", "dev")

APP_BASE_URL = os.getenv("APP_BASE_URL")

DASHBOARD_NAME = "MOJ AWS Showback Report"

# Auth config

AUTH_DISABLED = (os.getenv("AUTH_DISABLED") or "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Athena config

ATHENA_REGION = os.getenv("ATHENA_REGION")

ATHENA_ROLE = os.getenv("ATHENA_ROLE")

ATHENA_OUTPUT_LOCATION = os.getenv("ATHENA_OUTPUT_LOCATION")

ATHENA_WORKGROUP = os.getenv("ATHENA_WORKGROUP")

ATHENA_DATABASE = os.getenv("ATHENA_CACHE_DATABASE")

ATHENA_QUERY = os.getenv("ATHENA_CACHE_QUERY")

# Redis config

REDIS_HOST = os.getenv("REDIS_HOST", "")

REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

CACHE_TTL_SECONDS = int(
    os.getenv("ATHENA_CACHE_TTL_SECONDS", "3024000")
)

# Redis config validation

if APP_ENV != "local" and (not REDIS_HOST or not REDIS_PASSWORD):
    raise ValueError("Redis host and password must not be empty")

if CACHE_TTL_SECONDS <= 0:
    raise ValueError("Cache TTL and maximum size must be positive")