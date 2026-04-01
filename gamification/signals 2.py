"""
Django signals to automatically update gamification data.
"""

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .services import GamificationService


@receiver(user_logged_in)
def update_streak_on_login(sender, request, user, **kwargs):
    """
    Automatically update user's streak when they log in.
    Also checks for streak-based badges.
    """
    GamificationService.update_user_streak(user)
