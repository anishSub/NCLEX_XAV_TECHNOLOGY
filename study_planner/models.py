from django.db import models
from django.conf import settings
from categories.models import Categories
from django.utils import timezone


class StudyPlan(models.Model):
    """Main study plan configuration per user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_plan')
    exam_date = models.DateField(help_text="Target NCLEX exam date")
    daily_study_hours = models.IntegerField(default=2, help_text="Daily study goal in hours")
    study_streak = models.IntegerField(default=0, help_text="Consecutive days with completed tasks")
    last_study_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_plans'

    def __str__(self):
        return f"Study Plan - {self.user.email} (Exam: {self.exam_date})"


class StudyTask(models.Model):
    """Individual to-do items for study planning."""
    TASK_TYPES = [
        ('PRACTICE', 'Practice Questions'),
        ('REVIEW', 'Review Content'),
        ('MOCK_EXAM', 'Mock Exam'),
        ('CUSTOM', 'Custom Task'),
    ]
    
    PRIORITY_LEVELS = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    
    study_plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default='CUSTOM')
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, blank=True)
    
    scheduled_date = models.DateField()
    estimated_minutes = models.IntegerField(default=30, help_text="Estimated time in minutes")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    
    # Status tracking instead of simple boolean
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_minutes = models.IntegerField(null=True, blank=True, help_text="Actual time spent in minutes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_tasks'
        ordering = ['scheduled_date', '-priority', 'created_at']

    def __str__(self):
        status_icon = "✓" if self.status == 'COMPLETED' else "⏳" if self.status == 'IN_PROGRESS' else "☐"
        return f"{status_icon} {self.title} ({self.scheduled_date})"
    
    def mark_complete(self, actual_minutes=None):
        """Mark task as complete and update study streak."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if actual_minutes:
            self.actual_minutes = actual_minutes
        self.save()
        
        # Update study streak
        self.study_plan.update_streak()
    
    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = 'IN_PROGRESS'
        self.save()
    
    def mark_todo(self):
        """Mark task as to-do."""
        self.status = 'TODO'
        self.completed_at = None
        self.save()


class StudySession(models.Model):
    """Track actual study time and activities per day."""
    study_plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField()
    total_minutes = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_sessions'
        unique_together = ['study_plan', 'session_date']
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.study_plan.user.email} - {self.session_date} ({self.total_minutes} min)"


# Add method to StudyPlan for streak calculation
def update_streak(self):
    """Update study streak based on task completion."""
    today = timezone.now().date()
    
    # Check if there are completed tasks today
    completed_today = self.tasks.filter(
        status='COMPLETED',
        completed_at__date=today
    ).exists()
    
    if completed_today:
        # Check if last study was yesterday (consecutive)
        if self.last_study_date:
            if (today - self.last_study_date).days == 1:
                self.study_streak += 1
            elif (today - self.last_study_date).days > 1:
                # Streak broken, reset
                self.study_streak = 1
        else:
            self.study_streak = 1
        
        self.last_study_date = today
        self.save()

StudyPlan.update_streak = update_streak
