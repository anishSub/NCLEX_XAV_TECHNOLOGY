from django.urls import path
from . import views

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
]