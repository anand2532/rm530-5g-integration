"""Custom exceptions for RM530 5G Integration."""


class RM530Error(Exception):
    """Base exception for RM530 errors."""

    pass


class ModemNotFoundError(RM530Error):
    """Modem not found or not responding to AT commands."""

    pass


class NetworkConfigurationError(RM530Error):
    """NetworkManager configuration failed."""

    pass


class SerialCommunicationError(RM530Error):
    """Serial communication error with modem."""

    pass


class ConfigurationError(RM530Error):
    """Configuration file or parameter error."""

    pass


class SignalQualityError(RM530Error):
    """Error reading signal quality from modem."""

    pass
