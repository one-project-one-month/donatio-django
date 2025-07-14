from django.db import models


class NotificationType(models.TextChoices):
    FAILURE = "failure", "Failure"
    SUCCESS = "success", "Success"
    PENDING = "pending", "Pending"
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"
    DEBUG = "debug", "Debug"
    CRITICAL = "critical", "Critical"
    FATAL = "fatal", "Fatal"
    UNKNOWN = "unknown", "Unknown"
