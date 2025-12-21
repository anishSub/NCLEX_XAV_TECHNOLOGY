from django.db import models

class Scenarios(models.Model):
    title = models.CharField(max_length=255)
    exhibits = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scenarios'

    def __str__(self):
        return self.title