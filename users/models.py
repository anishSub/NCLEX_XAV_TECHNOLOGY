from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    subscription_status = models.BooleanField(default=False)
    performance_stats = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username