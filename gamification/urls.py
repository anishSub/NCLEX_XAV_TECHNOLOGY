from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('badges/', views.badges_view, name='badges'),
    path('api/stats/', views.profile_stats_api, name='stats_api'),
]
