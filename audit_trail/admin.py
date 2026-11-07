from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "actor",
        "action",
        "target_model",
        "object_pk",
        "description",
    )

    list_filter = (
        "action",
        "target_model",
        "timestamp",
    )

    search_fields = (
        "actor__username",
        "target_model",
        "object_pk",
        "description",
    )

    readonly_fields = (
        "actor",
        "action",
        "target_model",
        "object_pk",
        "description",
        "changes",
        "ip_address",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

