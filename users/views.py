from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import StudentSignUpForm
from .models import Users, StudentProfile

# --- REGISTER VIEW ---
class RegisterView(CreateView):
    form_class = StudentSignUpForm
    template_name = 'users/registration.html' # Matches your folder structure
    success_url = reverse_lazy('login') 
    
    def form_valid(self, form):
        # 1. Create User instance but don't save to DB yet
        user = form.save(commit=False)
        
        # 2. Sync username with email (since you use email to login)
        user.username = user.email 
        
        # 3. Force role to STUDENT
        user.role = Users.Role.STUDENT
        user.save()
        
        # 4. Create Student Profile
        # We handle this manually to ensure it exists immediately
        if not hasattr(user, 'student_profile'):
            StudentProfile.objects.create(user=user)
        
        # 5. Log the user in immediately
        # backend='...' fixes bugs when logging in right after sign up
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        messages.success(self.request, 'Registration successful! Welcome to NCLEX Core.')
        return redirect('home')

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please correct the errors below.")
        return super().form_invalid(form)


# --- LOGIN VIEW ---
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        
        # 1. ADMIN Redirect
        if user.is_superuser or user.role == Users.Role.ADMIN:
            # Redirects to the Jazzmin Admin Panel
            return reverse_lazy('admin:index')
            
        # 2. STUDENT Redirect
        elif user.role == Users.Role.STUDENT:
            return reverse_lazy('home')
        
        # 3. Default Fallback
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


# --- LOGOUT VIEW ---
class CustomLogoutView(LogoutView):
    next_page = 'login' 
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


# --- PROFILE VIEW ---
@login_required
def profile_view(request):
    """User profile page – view and update personal info."""
    user = request.user
    profile, _ = StudentProfile.objects.get_or_create(user=user)

    # Try to pull gamification stats
    try:
        from gamification.services import GamificationService
        gam_profile = GamificationService.get_or_create_profile(user)
        user_rank = GamificationService.get_user_rank(user)
        badges = GamificationService.get_user_badges(user)
    except Exception:
        gam_profile = None
        user_rank = '—'
        badges = []

    if request.method == 'POST':
        # Update basic info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.bio = request.POST.get('bio', profile.bio)

        # Profile image upload
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        user.save()
        profile.save()

        # Optional password change
        current_pw = request.POST.get('current_password')
        new_pw = request.POST.get('new_password')
        confirm_pw = request.POST.get('confirm_password')
        if current_pw and new_pw:
            if not user.check_password(current_pw):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm_pw:
                messages.error(request, 'New passwords do not match.')
            else:
                user.set_password(new_pw)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {
        'profile': profile,
        'gam_profile': gam_profile,
        'user_rank': user_rank,
        'badges_count': len(badges),
    }
    return render(request, 'users/profile.html', context)