from django.db import models
from exam_sessions.models import ExamSessions
from questions.models import Questions

class UserResponses(models.Model):
    session = models.ForeignKey(ExamSessions, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    selected_options = models.JSONField(default=list)
    is_correct = models.BooleanField()
    time_taken = models.FloatField()

    class Meta:
        db_table = 'user_responses'

    def __str__(self):
        return f"Response {self.id} for Session {self.session_id}"