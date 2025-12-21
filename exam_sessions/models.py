from django.db import models
from django.conf import settings

class ExamSessions(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    current_theta = models.FloatField(default=0.0)
    question_history = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'exam_sessions'

    def __str__(self):
        return f"Session {self.id} - {self.user.username}"