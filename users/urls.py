from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # --- Password Reset (Using Built-in Views with Custom Templates) ---
    
    # 1. Enter Email Page
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='forget_password/password_reset_form.html',
            email_template_name='forget_password/password_reset_email.html',
            subject_template_name='forget_password/password_reset_subject.txt'
        ), 
        name='password_reset'),

    # 2. "Email Sent" Success Page
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='forget_password/password_reset_done.html'
        ), 
        name='password_reset_done'),

    # 3. Enter New Password Page (Link from Email)
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='forget_password/password_reset_confirm.html'
        ), 
        name='password_reset_confirm'),

    # 4. "Password Changed" Success Page
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='forget_password/password_reset_complete.html'
        ), 
        name='password_reset_complete'),
]