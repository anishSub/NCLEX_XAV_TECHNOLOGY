from django.db import models
from scenarios.models import Scenarios
from categories.models import Categories

class Questions(models.Model):
    text = models.TextField()
    type = models.CharField(max_length=50)
    options = models.JSONField(default=list)
    correct_option_ids = models.JSONField(default=list)
    rationale = models.TextField(blank=True)
    difficulty_logit = models.FloatField()
    parent_scenario = models.ForeignKey(Scenarios, on_delete=models.CASCADE, null=True, blank=True)
    category_ids = models.ManyToManyField(Categories, blank=True)

    class Meta:
        db_table = 'questions'

    def __str__(self):
        return f"{self.type}: {self.text[:50]}"