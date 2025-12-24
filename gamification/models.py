from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserGameProfile(models.Model):
    """
    Stores gamification data for each user.
    One profile per user - tracks points, streaks, level.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='game_profile')
    
    # Points & Level
    total_points = models.IntegerField(default=0, db_index=True)
    level = models.IntegerField(default=1)
    
    # Streaks
    current_streak = models.IntegerField(default=0, db_index=True)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    
    # Stats
    total_questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gamification_profile'
        indexes = [
            models.Index(fields=['-total_points']),  # For leaderboard
            models.Index(fields=['-current_streak']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({self.total_points} pts)"
    
    @property
    def average_score(self):
        """Calculate average score percentage"""
        if self.total_questions_answered == 0:
            return 0
        return round((self.correct_answers / self.total_questions_answered) * 100, 1)
    
    @property
    def points_to_next_level(self):
        """Points needed for next level"""
        next_level_threshold = self.get_level_threshold(self.level + 1)
        return next_level_threshold - self.total_points
    
    @staticmethod
    def get_level_threshold(level):
        """Get points required for a specific level (exponential)"""
        if level == 1:
            return 0
        return 100 * (level - 1) ** 2  # Exponential scaling
    
    def add_points(self, points, reason=""):
        """Add points and check for level up"""
        self.total_points += points
        
        # Check for level up
        while self.total_points >= self.get_level_threshold(self.level + 1):
            self.level += 1
        
        self.save()
    
    def update_streak(self):
        """Update daily streak - called on login"""
        today = timezone.now().date()
        
        # First time
        if not self.last_active_date:
            self.current_streak = 1
            self.last_active_date = today
            self.add_points(5, "First login")
            self.save()
            return True
        
        # Already updated today
        if self.last_active_date == today:
            return False
        
        # Check if consecutive day
        yesterday = today - timedelta(days=1)
        if self.last_active_date == yesterday:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.add_points(5, "Daily login")
        else:
            # Streak broken
            self.current_streak = 1
        
        self.last_active_date = today
        self.save()
        return True


class UserBadge(models.Model):
    """
    Tracks badges earned by users.
    Each badge can only be earned once per user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_code = models.CharField(max_length=50, db_index=True)
    earned_date = models.DateTimeField(auto_now_add=True)
    points_awarded = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'gamification_badge'
        unique_together = ['user', 'badge_code']
        indexes = [
            models.Index(fields=['user', 'badge_code']),
            models.Index(fields=['-earned_date']),
        ]
        ordering = ['-earned_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge_code}"


class DailyActivity(models.Model):
    """
    Tracks user activity by day for analytics.
    Used for streak validation and activity graphs.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField(db_index=True)
    questions_answered = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'gamification_daily_activity'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
