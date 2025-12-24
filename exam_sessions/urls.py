from django.urls import path
from . import views
from . import practice_views

urlpatterns = [
    # Start a new exam session
    path('start/', views.start_exam_view, name='start_exam'),
    
    # API: Get first question for a session
    path('api/session/<int:session_id>/first-question/', 
         views.get_first_question_api, 
         name='first_question'),
    
    # API: Submit answer and get next question
    path('api/session/<int:session_id>/submit/', 
         views.SubmitMockAnswerAPI.as_view(),
         name='submit_answer'),
    
    # The human-friendly results page
    path('results/<int:session_id>/', views.exam_results_view, name='exam_results'),
    
    # The API endpoint the chart will call
    path('api/performance-data/<int:session_id>/', views.performance_data_api, name='performance_data'),
    
    # ==================== PRACTICE MODE ROUTES ====================
    path('practice/categories/', practice_views.practice_categories_view, name='practice_categories'),
    path('practice/start/', practice_views.start_practice_session, name='start_practice'),
    path('practice/session/<int:session_id>/', practice_views.take_practice_exam, name='take_practice_exam'),
    path('practice/api/session/<int:session_id>/first-question/', practice_views.get_practice_first_question, name='practice_first_question'),
    path('practice/api/session/<int:session_id>/submit/', practice_views.submit_practice_answer, name='practice_submit_answer'),
    path('practice/results/<int:session_id>/', practice_views.practice_results_view, name='practice_results'),
]