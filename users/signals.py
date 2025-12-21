from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Users, StudentProfile

@receiver(user_signed_up)
def social_signup_process(request, user, **kwargs):
    # 1. Set Role to STUDENT (if it's missing)
    # This handles the case where Google creates the user but doesn't set a role
    if not user.role:
        user.role = Users.Role.STUDENT
        user.save()

    # 2. Create the Student Profile automatically
    if not hasattr(user, 'student_profile'):
        StudentProfile.objects.create(
            user=user,
            phone_number="",  # Social login doesn't provide this
            bio="Joined via Social Login"
        )