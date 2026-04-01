from .models import StudyPlan


def study_plan_navigation(request):
    has_study_plan = False

    if getattr(request, "user", None) and request.user.is_authenticated:
        has_study_plan = StudyPlan.objects.filter(user=request.user).exists()

    return {
        "has_study_plan": has_study_plan,
        "dashboard_nav_label": "Dashboard" if has_study_plan else "Plan Setup",
        "dashboard_nav_url": "study_planner" if has_study_plan else "setup_study_plan",
    }
