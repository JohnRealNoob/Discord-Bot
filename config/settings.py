from discord import Intents

# Command prefix for traditional commands
PREFIX = "!"

# Discord intents configuration
INTENTS = Intents.default()
INTENTS.message_content = True  # Enable for prefix commands
INTENTS.members = True         # Enable for member-related events

# Cogs to exclude from auto-loading
EXCLUDED_COGS = {"music.py", "__init__.py"}