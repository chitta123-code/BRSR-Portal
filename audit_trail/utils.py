from .models import AuditLog


def record_audit(
    request,
    action,
    instance,
    description,
    changes=None,
):
    """
    Record an action on a Django model instance.
    Never include passwords, tokens, or other secrets in changes.
    """

    user = request.user if request.user.is_authenticated else None

    ip_address = request.META.get("REMOTE_ADDR")

    return AuditLog.objects.create(
        actor=user,
        action=action,
        target_model=instance._meta.label,
        object_pk=str(instance.pk),
        description=description,
        changes=changes or {},
        ip_address=ip_address,
    )

