from .views import home, hello_api
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    
    # The API Endpoint
    path('api/hello/', hello_api, name='hello_api'),
]