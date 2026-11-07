from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .models import AuditLog


@login_required
def audit_trail_dashboard(request):
    allowed = (
        request.user.is_superuser
        or request.user.groups.filter(
            name__in=["Manager", "Reviewer"]
        ).exists()
    )

    if not allowed:
        raise PermissionDenied(
            "You do not have permission to view the audit trail."
        )

    logs = AuditLog.objects.select_related(
        "actor"
    ).all()

    action = request.GET.get("action", "").strip()
    search = request.GET.get("q", "").strip()

    if action:
        logs = logs.filter(action=action)

    if search:
        from django.db.models import Q

        logs = logs.filter(
            Q(actor__username__icontains=search)
            | Q(target_model__icontains=search)
            | Q(object_pk__icontains=search)
            | Q(description__icontains=search)
        )

    return render(
        request,
        "audit_trail/dashboard.html",
        {
            "logs": logs[:500],
            "selected_action": action,
            "search_query": search,
            "action_choices": AuditLog.ACTION_CHOICES,
        },
    )

