from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_page, name='game_page'),
    path('play/', views.play_game, name='play_game'),
    path('api/categories/', views.get_categories_api, name='game_categories_api'),
    path('api/questions/', views.get_questions_api, name='game_questions_api'),
]
