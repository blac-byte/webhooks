from django.db import models



class Event(models.Model):

    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        VERIFIED = "verified", "Verified"
        UNSUPPORTED = "unsupported", "Unsupported"
        PROCESSING = "processing", "Processing"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    source = models.CharField(max_length=50)
    external_event_id = models.CharField(max_length=255)
    raw_payload = models.JSONField()
    normalized_payload = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("source", "external_event_id")
