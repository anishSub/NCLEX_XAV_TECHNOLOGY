from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from .models import Users

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        
        # 1. Admin -> Jazzmin Dashboard
        if user.is_superuser or user.role == Users.Role.ADMIN:
            return resolve_url('admin:index')
            
        # 2. Student -> Home Page
        elif user.role == Users.Role.STUDENT:
            return resolve_url('home')
            
        return resolve_url('home')