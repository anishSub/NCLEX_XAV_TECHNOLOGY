from django.db import models
from scenarios.models import Scenarios
# Assuming Categories is in a 'categories' app
# from categories.models import Categories 
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
import uuid
import os


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
    
    # ========== SCENARIO ENHANCEMENT FIELDS ==========
    # For dynamic exhibit updates in unfolding case studies
    exhibit_updates = models.JSONField(
        default=dict,
        blank=True,
        help_text="New or updated exhibit tabs to show with this question. Format: {'Tab_Name': 'content', 'Labs_1200': 'New lab results...'}"
    )
    
    # For sequential question delivery within scenarios
    scenario_question_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Question number within scenario (1-6 for NCLEX NGN). Questions will be delivered in this order."
    )
    
    # For tracking NCLEX Clinical Judgment Measurement Model (NCJMM) functions
    clinical_judgment_function = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('RECOGNIZE_CUES', 'Recognize Cues'),
            ('ANALYZE_CUES', 'Analyze Cues'),
            ('PRIORITIZE_HYPOTHESES', 'Prioritize Hypotheses'),
            ('GENERATE_SOLUTIONS', 'Generate Solutions'),
            ('TAKE_ACTIONS', 'Take Actions'),
            ('EVALUATE_OUTCOMES', 'Evaluate Outcomes'),
        ],
        help_text="NCJMM Clinical Judgment Function this question tests (for scenario questions)"
    )

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
            
        # UNIVERSAL BASE64 IMAGE HANDLING
        # Detect if 'options' has a Base64 image string and convert it to a file.
        # This allows pasting images in ANY admin form (Questions, Scenarios, HotSpot).
        if self.options and isinstance(self.options, dict):
            current_url = self.options.get('image_url', '')
            if current_url and current_url.startswith('data:image'):
                try:
                    # Parse Base64: "data:image/png;base64,iVBOR..."
                    header, encoded = current_url.split(';base64,')
                    # Get extension (default to png if parsing fails)
                    extension = 'png'
                    if 'image/' in header:
                        extension = header.split('image/')[1]
                    
                    # Generate unique filename
                    filename = f"hotspot_pasted_{uuid.uuid4().hex[:8]}.{extension}"
                    file_path = f"hotspot_images/{filename}"
                    
                    # Decode data
                    image_data = base64.b64decode(encoded)
                    
                    # Save to storage (Standard Django Storage)
                    saved_path = default_storage.save(file_path, ContentFile(image_data))
                    saved_url = default_storage.url(saved_path)

                    # FALLBACK: If MEDIA_URL wasn't set when this ran, it might return just path.
                    # We force /media/ prefix if it's missing and not an S3 URL.
                    from django.conf import settings
                    if not saved_url.startswith('http') and not saved_url.startswith(settings.MEDIA_URL):
                        saved_url = settings.MEDIA_URL + saved_path
                    
                    # Update option with real URL
                    self.options['image_url'] = saved_url
                    
                    print(f"✅ Converted Base64 image to file in Questions.save(): {saved_url}")
                    
                except Exception as e:
                    print(f"❌ Error converting Base64 image in Questions.save(): {e}")
                    
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

        # Hot Spot Validation
        if question_type_code in ['HOT_SPOT', 'HOT SPOT']:
            # 1. Check for Image URL in options
            if not isinstance(self.options, dict) or not self.options.get('image_url'):
                raise ValidationError("Hot Spot questions must have an 'image_url' in the options. Use the Hot Spot tool to upload/paste an image.")
            
            # 2. Check for Coordinates in correct_option_ids
            # correct_option_ids might be a list (legacy) or dict (new Hot Spot format)
            hotspot_data = self.correct_option_ids
            if isinstance(hotspot_data, str):
                 # Try to parse if it's a string
                 import json
                 try:
                     hotspot_data = json.loads(hotspot_data)
                 except:
                     pass
            
            if not isinstance(hotspot_data, dict):
                 raise ValidationError("Hot Spot answer data must be a JSON object with coordinates. Click the image in the Hot Spot tool to set the correct answer.")
            
            if 'center_x' not in hotspot_data or 'center_y' not in hotspot_data:
                raise ValidationError("Hot Spot questions must have a defined target zone. Click the image to set the correct answer.")


class HotSpotQuestion(Questions):
    """
    Proxy model for Hot Spot questions to give them a dedicated admin interface.
    This allows for a cleaner, image-focused UI without adding db tables.
    """
    class Meta:
        proxy = True
        verbose_name = 'Hot Spot Question'
        verbose_name_plural = 'Hot Spot Questions'
