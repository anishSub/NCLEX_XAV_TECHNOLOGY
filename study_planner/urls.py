from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard
    path('', views.planner_dashboard, name='study_planner'),
    path('setup/', views.setup_study_plan, name='setup_study_plan'),
    
    # Task CRUD
    path('api/tasks/create/', views.create_task, name='create_task'),
    path('api/tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('api/tasks/<int:task_id>/status/', views.update_task_status, name='update_task_status'),
    path('api/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    
    # Calendar data
    path('api/calendar/<str:view_type>/', views.get_calendar_tasks, name='calendar_tasks'),
    
    # Stats
    path('api/stats/', views.get_study_stats, name='study_stats'),
    
    # Smart Recommendations
    path('api/recommendations/', views.get_recommendations, name='get_recommendations'),
    path('api/recommendations/create-task/', views.create_recommendation_task, name='create_recommendation_task'),
]
