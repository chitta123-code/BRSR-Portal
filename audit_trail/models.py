from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("SUBMIT", "Submit"),
        ("REVIEW", "Review"),
        ("APPROVE", "Approve"),
        ("REJECT", "Reject"),
        ("VERIFY", "Verify Evidence"),
        ("IMPORT", "Import Data"),
        ("EXPORT", "Export"),
        ("DELETE", "Delete"),
        ("OTHER", "Other"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="brsr_audit_logs",
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        default="OTHER",
        db_index=True,
    )

    target_model = models.CharField(max_length=100)
    object_pk = models.CharField(max_length=100, blank=True)

    description = models.TextField()

    # Store explicitly supplied before/after values as JSON.
    changes = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Trail Entry"
        verbose_name_plural = "Audit Trail Entries"

    def __str__(self):
        username = self.actor.username if self.actor else "Unknown user"
        return f"{username} - {self.action} - {self.target_model}"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Audit log entries cannot be edited.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit log entries cannot be deleted.")

