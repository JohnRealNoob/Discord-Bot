from typing import Optional

class ConfigError(Exception):
    """Custom exception class for configuration-related errors."""
    def __init__(self, message: str, error_code: Optional[int] = None):
        """
        Initialize ConfigError with a message and optional error code.
        
        Args:
            message (str): The error message to display
            error_code (int, optional): A specific code for categorizing the error
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the error."""
        if self.error_code is not None:
            return f"ConfigError [{self.error_code}]: {self.message}"
        return f"ConfigError: {self.message}"