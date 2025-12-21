from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Users(AbstractUser):
    """
    Custom User Model responsible for Authentication (Email/Password) and Role.
    """
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"

    base_role = Role.STUDENT
    
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(unique=True)  # Used for login
    
    # Set email as the unique identifier for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Required for 'createsuperuser' command

    def save(self, *args, **kwargs):
        # Automatically set role if creating a new user
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class StudentProfile(models.Model):
    """
    Profile Model responsible for NCLEX-specific data (Bio, Stats, Subscription).
    Linked One-to-One with the User.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    
    # --- Basic Info ---
    profile_image = models.ImageField(upload_to='students/profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Your study goals")
    
    # --- NCLEX / App Specific ---
    target_exam_date = models.DateField(null=True, blank=True)
    is_subscribed = models.BooleanField(default=False)
    
    # --- Performance Snapshot ---
    # We store a summary here so we don't have to calculate it on every page load
    performance_stats = models.JSONField(default=dict, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


# --- SIGNALS ---
# Automatically create a StudentProfile when a new User (Student) registers
@receiver(post_save, sender=Users)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == Users.Role.STUDENT:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=Users)
def save_student_profile(sender, instance, **kwargs):
    if instance.role == Users.Role.STUDENT:
        # Ensure profile exists before saving (in case it was manually deleted)
        if hasattr(instance, 'student_profile'):
            instance.student_profile.save()