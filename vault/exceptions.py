"""Custom exceptions for the vault package"""


class WrongKV2Configuration(Exception):
    """
    Raised when the configuration for a kv2 engine is incorrect.

    Args:
        message (str): The error message.

    Example:
        >>> try:
        ...     raise WrongKV2Configuration("Incorrect kv2 engine configuration")
        ... except WrongKV2Configuration as e:
        ...     print(e)
        Incorrect kv2 engine configuration
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)
