from django.db import models
from scenarios.models import Scenarios
# Assuming Categories is in a 'categories' app
# from categories.models import Categories 
from django.core.exceptions import ValidationError

class Questions(models.Model):
    """
    Child model representing individual NCLEX items.
    Includes the difficulty_logit (b) used for the Rasch probability formula.
    """
    text = models.TextField()
    type = models.CharField(max_length=50) # e.g., SATA, MATRIX, HOT_SPOT
    options = models.JSONField(default=list) # Flexible JSON for NGN patterns
    correct_option_ids = models.JSONField(default=list)
    rationale = models.TextField(blank=True)
    
    # Critical for CAT: Logit scale typically -3.0 to +3.0
    difficulty_logit = models.FloatField(default=0.0)
    
    # Parent-Child link for Unfolding Case Studies
    parent_scenario = models.ForeignKey(
        Scenarios, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='questions'
    )
    


    def clean(self):
    # Logic: If MCQ, ensure only one correct answer is provided
        if self.type == 'MCQ' and len(self.correct_option_ids) != 1:
            raise ValidationError("MCQ questions must have exactly one correct answer.")
        
        # Logic: Ensure options are actually provided
        if not self.options:
            raise ValidationError("You must provide the 'options' JSON.")
    
    # Link questions to categories for practice mode
    category_ids = models.ManyToManyField('categories.Categories', blank=True, related_name='questions')


    class Meta:
        db_table = 'questions'

    def __str__(self):
        return f"{self.type}: {self.text[:50]}"
    
    
