from django.db import models
from scenarios.models import Scenarios
# Assuming Categories is in a 'categories' app
# from categories.models import Categories 
from django.core.exceptions import ValidationError


class QuestionType(models.Model):
    """
    Stores all available question types for the NCLEX platform.
    Allows dynamic addition of new question types through admin panel.
    """
    code = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Internal code used in system (e.g., 'SATA', 'MCQ')"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="User-friendly name displayed in admin (e.g., 'Select All That Apply')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this question type and when to use it"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Deactivate to hide from question creation without deleting"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question_types'
        ordering = ['display_name']
        verbose_name = 'Question Type'
        verbose_name_plural = 'Question Types'

    def __str__(self):
        return f"{self.display_name} ({self.code})"


class Questions(models.Model):
    """
    Child model representing individual NCLEX items.
    Includes the difficulty_logit (b) used for the Rasch probability formula.
    """
    text = models.TextField()
    
    # NEW: ForeignKey to QuestionType for dynamic type management
    question_type = models.ForeignKey(
        QuestionType,
        on_delete=models.PROTECT,  # Prevent deleting types that are in use
        related_name='questions',
        null=True,  # Temporary for migration
        blank=True,
        help_text="Select the question type from the dropdown or add a new type"
    )
    
    # OLD: Keep for backward compatibility during migration
    type = models.CharField(
        max_length=50, 
        blank=True,
        help_text="DEPRECATED: Use question_type field instead"
    )
    
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
    
    # Link questions to categories for practice mode
    category_ids = models.ManyToManyField('categories.Categories', blank=True, related_name='questions')

    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        # Use new question_type if available, otherwise fall back to old type field
        type_display = self.question_type.code if self.question_type else self.type
        return f"{type_display}: {self.text[:50]}"
    
    def save(self, *args, **kwargs):
        """Auto-sync type field with question_type for backward compatibility"""
        if self.question_type:
            self.type = self.question_type.code
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validation logic for questions"""
        # Use question_type if available, otherwise use old type field
        question_type_code = self.question_type.code if self.question_type else self.type
        
        # Logic: If MCQ, ensure only one correct answer is provided
        if question_type_code == 'MCQ' and len(self.correct_option_ids) != 1:
            raise ValidationError("MCQ questions must have exactly one correct answer.")
        
        # Logic: Ensure options are actually provided
        if not self.options:
            raise ValidationError("You must provide the 'options' JSON.")
