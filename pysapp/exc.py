# Warnings

class PysappDeprecationWarning(DeprecationWarning):
    """Issued once per usage of a deprecated API."""


class PysappPendingDeprecationWarning(PendingDeprecationWarning):
    """Issued once per usage of a deprecated API."""


class PysappWarning(RuntimeWarning):
    """Issued at runtime."""