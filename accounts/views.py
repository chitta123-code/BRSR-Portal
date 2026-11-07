from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect, render


def portal_login(request):
    """
    Main BRSR / ESG portal login-selection page.
    """

    if request.user.is_authenticated:
        return redirect("role_dashboard")

    return render(
        request,
        "accounts/portal_login.html"
    )


def role_dashboard(request):
    user = request.user

    if user.groups.filter(name="Manager").exists():
        print("ROLE RESULT: MANAGER")
        return redirect("manager_dashboard")

    if user.groups.filter(name="Data Entry").exists():
        print("ROLE RESULT: DATA ENTRY")
        return redirect("esg_dashboard")

    if user.groups.filter(name="ESG Analyst").exists():
        print("ROLE RESULT: ESG ANALYST")
        return redirect("esg_dashboard")

    if user.groups.filter(name="Reviewer").exists():
        print("ROLE RESULT: REVIEWER")
        return redirect("reviewer_dashboard")

    if user.is_superuser:
        print("ROLE RESULT: SUPERUSER")
        return redirect("admin:index")

    print("ROLE RESULT: INVALID")
    logout(request)

    return render(
        request,
        "accounts/login.html",
        {
            "error_message": (
                "Your account does not have a valid BRSR / ESG role. "
                "Please contact the administrator."
            )
        }
    )