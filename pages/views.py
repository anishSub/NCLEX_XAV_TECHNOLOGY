from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from questions.models import Questions
from categories.models import Categories
from users.models import Users


def home(request):
    """Home page — passes live platform stats to the template."""
    context = {
        'total_questions': Questions.objects.count(),
        'total_categories': Categories.objects.count(),
        'total_students': Users.objects.filter(role=Users.Role.STUDENT).count(),
    }
    # If user is authenticated, pull their gamification data
    if request.user.is_authenticated:
        try:
            from gamification.services import GamificationService
            gam = GamificationService.get_or_create_profile(request.user)
            context['user_gam'] = gam
        except Exception:
            context['user_gam'] = None
    return render(request, 'pages/home.html', context)


@api_view(['GET'])
def hello_api(request):
    data = {
        "message": "Welcome to NCLEX XAV API!",
        "status": "Success",
        "developer": "Anish"
    }
    return Response(data)