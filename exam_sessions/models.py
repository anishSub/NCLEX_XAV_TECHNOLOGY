from django.db import models
from django.conf import settings

class ExamSessions(models.Model):
    """
    The core engine storage for Computerized Adaptive Testing (CAT).
    Tracks the narrowing 95% Confidence Interval.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Ongoing, PASS, or FAIL
    status = models.CharField(max_length=50, default='Ongoing')
    
    # Adaptive Math Fields
    current_theta = models.FloatField(default=0.0) # Student's ability estimate (theta)
    
    # Sum of P*(1-P) used to calculate standard error
    total_information = models.FloatField(default=0.01) 
    
    # Standard Error (SE) for the 95% Confidence Rule
    # Initialized at 1.0 for high uncertainty
    standard_error = models.FloatField(default=1.0)
    
    # Stores history for Chart.js: [{"theta": 0.1, "se": 0.8, "is_correct": true}, ...]
    question_history = models.JSONField(default=list, blank=True)
    
    # Session type: ADAPTIVE (95% confidence CAT) or PRACTICE (category-based)
    SESSION_TYPES = [
        ('ADAPTIVE', 'Adaptive Exam'),
        ('PRACTICE', 'Practice Mode'),
    ]
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='ADAPTIVE')
    
    # For practice mode: selected category IDs
    selected_categories = models.JSONField(default=list, blank=True)
    
    # For practice mode: total questions to practice
    total_questions = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'exam_sessions'

    def __str__(self):
        return f"Session {self.id} - {self.user.email}"