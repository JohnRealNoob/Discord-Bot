import os
from dotenv import load_dotenv
from .errors import ConfigError

# Load .env file from project root
load_dotenv()

def get_env_var(name: str, required: bool = True, default: str | None = None) -> str:
    """Safely get an environment variable with validation."""
    value = os.getenv(name, default)
    if required and value is None:
        raise ConfigError(f"Required environment variable '{name}' not found", error_code=1001)
    return value

def validate_discord_id(value: str) -> int:
    """Validate that a string is a valid Discord ID."""
    try:
        id_int = int(value)
        if not (10**16 <= id_int <= 10**18):  # Rough Discord ID range
            raise ConfigError(f"Invalid Discord ID '{value}': must be 17-18 digits", error_code=1002)
        return id_int
    except ValueError:
        raise ConfigError(f"Invalid Discord ID '{value}': must be an integer", error_code=1003)

# Define environment variables
try:
    TOKEN = get_env_var("DISCORD_TOKEN")
    OWNER_ID = validate_discord_id(get_env_var("OWNER_ID"))
    LAVALINK_HOST = get_env_var("LAVALINK_HOST")
    LAVALINK_PASSWORD = get_env_var("LAVALINK_PASSWORD")
    LAVALINK_PORT = int(get_env_var("LAVALINK_PORT"))
except ConfigError as e:
    raise  # Re-raise to be caught by the main application