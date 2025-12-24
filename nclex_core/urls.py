"""
URL configuration for nclex_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 1. Your Custom Login/Register App
    path('auth/', include('users.urls')), 
    
    # 2. REQUIRED: The Magic Allauth URLs for Google/Facebook
    path('accounts/', include('allauth.urls')),
    
    # 3. Exam Sessions (Adaptive Testing)
    path('exam/', include('exam_sessions.urls')),
    
    # 4. Study Planner (Calendar & To-Do List)
    path('planner/', include('study_planner.urls')),
    
    # 5. Subscriptions & Pricing
    path('subscriptions/', include('subscriptions.urls')),
    
    path('', include('pages.urls')),  # Home Page
    
]
