from django.contrib import admin
from django.db import models
from django import forms
from .models import Questions, QuestionType


# ========== QUESTION TYPE ADMIN (Separate Page for Managing Types) ==========
@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    """
    DEDICATED PAGE for managing question types.
    Use this page to add, edit, or deactivate question types.
    """
    list_display = ('code', 'display_name', 'is_active', 'question_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'display_name', 'description')
    ordering = ('display_name',)
    
    # Enhanced add/edit form
    fieldsets = (
        (None, {
            'fields': ('code', 'display_name'),
            'description': '✨ Add a new question type that will appear in the Questions dropdown'
        }),
        ('Description', {
            'fields': ('description',),
            'description': 'Optional: Describe when to use this question type'
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Uncheck to hide this type from question creation'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # Actions
    actions = ['activate_types', 'deactivate_types']
    
    def activate_types(self, request, queryset):
        """Activate selected question types"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} question type(s) activated.")
    activate_types.short_description = "Activate selected types"
    
    def deactivate_types(self, request, queryset):
        """Deactivate selected question types"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} question type(s) deactivated.")
    deactivate_types.short_description = "Deactivate selected types"
    
    def question_count(self, obj):
        """Show how many questions use this type"""
        return obj.questions.count()
    question_count.short_description = "Questions"
    question_count.admin_order_field = 'questions__count'


# ========== QUESTIONS ADMIN (Separate Page for Viewing/Searching Questions) ==========
@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    """
    DEDICATED PAGE for viewing and searching questions.
    Use filters to search by type, difficulty, scenario, etc.
    To add new question types, go to the Question Types admin page.
    """
    
    # REMOVED autocomplete_fields to prevent adding types from this page
    # Users must go to Question Types page to add new types
    
    # Enhanced search
    search_fields = (
        'text',  # Search by question text
        'id',  # Search by ID
        'question_type__code',  # Search by type code
        'question_type__display_name',  # Search by type name
    )
    
    # Clean list display focused on viewing questions
    list_display = (
        'id',
        'get_question_type_badge',
        'short_text',
        'difficulty_logit',
        'parent_scenario',
        'get_category_count',
        'get_status'
    )
    
    # Enhanced filters for searching
    list_filter = (
        ('question_type', admin.RelatedOnlyFieldListFilter),  # Only show types that have questions
        'difficulty_logit',
        ('parent_scenario', admin.RelatedOnlyFieldListFilter),
        'category_ids',
    )
    
    # Enable bulk actions
    actions = ['duplicate_questions', 'export_questions']
    
    # Organized edit form
    # Custom field labels and defaults
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['text'].label = 'Place question here'
        form.base_fields['options'].label = 'Options (answer choices in JSON format)'
        form.base_fields['correct_option_ids'].label = 'Correct option IDs (which answers are correct)'
        form.base_fields['rationale'].label = 'Rationale (explain why this answer is correct)'
        form.base_fields['category_ids'].label = 'Category IDs (select content areas for this question)'
        
        # Pre-fill options with template for new questions
        if not obj:  # Only for new questions, not editing existing ones
            form.base_fields['options'].initial = [
                {"id": "A", "text": ""},
                {"id": "B", "text": ""},
                {"id": "C", "text": ""},
                {"id": "D", "text": ""}
            ]
            form.base_fields['correct_option_ids'].initial = [""]
        
        return form
    
    fieldsets = (
        ('Question Type', {
            'fields': ('question_type',),
            'description': 'Select the question type from the dropdown or add a new type'
        }),
        ('Question Content', {
            'fields': ('text', 'options', 'correct_option_ids', 'rationale'),
        }),
        ('Difficulty & Classification', {
            'fields': ('difficulty_logit', 'category_ids'),
        }),
        ('Scenario Link', {
            'fields': ('parent_scenario',),
            'classes': ('collapse',),
        }),
        ('System Fields (Legacy)', {
            'fields': ('type',),
            'classes': ('collapse',),
            'description': '⚠️ Legacy field - kept for backward compatibility. Use question_type instead.'
        }),
    )
    
    readonly_fields = ('type',)
    filter_horizontal = ('category_ids',)

    # Standard Textarea for JSON fields - Proven to work in Scenarios
    formfield_overrides = {
        models.JSONField: {'widget': forms.Textarea(attrs={
            'rows': 15, 
            'style': 'width: 100%; font-family: monospace;',
            'placeholder': 'Enter JSON data here...'
        })},
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Force Textarea for specific fields
        if db_field.name in ['options', 'correct_option_ids', 'exhibit_updates']:
            kwargs['widget'] = forms.Textarea(attrs={
                'rows': 10, 
                'style': 'width: 100%; font-family: monospace;',
                'placeholder': f'Enter JSON for {db_field.name}...'
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    # List per page
    list_per_page = 25
    
    # Custom display methods
    def get_question_type_badge(self, obj):
        """Display question type with color coding"""
        if obj.question_type:
            type_code = obj.question_type.code
            # Color code by type
            colors = {
                'MCQ': '🟦',
                'SATA': '🟩',
                'DRAG_DROP_RATIONALE': '🟨',
                'MATRIX_MULTIPLE': '🟧',
                'DROPDOWN_RATIONALE': '🟪',
                'HOT_SPOT': '🟥',
                'HIGHLIGHT_TEXT': '⬜',
            }
            badge = colors.get(type_code, '⚪')
            return f"{badge} {obj.question_type.display_name}"
        return obj.type or "❌ No Type"
    get_question_type_badge.short_description = "Type"
    get_question_type_badge.admin_order_field = 'question_type__display_name'
    
    def short_text(self, obj):
        """Truncate question text for list view"""
        return obj.text[:75] + "..." if len(obj.text) > 75 else obj.text
    short_text.short_description = "Question"
    
    # Custom Media
    class Media:
        js = ('questions/js/hotspot_coordinator.js',)

    def get_category_count(self, obj):
        """Show number of categories"""
        count = obj.category_ids.count()
        return f"{count} categories" if count != 1 else "1 category"
    get_category_count.short_description = "Categories"
    
    def get_status(self, obj):
        """Show question status"""
        if not obj.question_type:
            return "⚠️ Missing Type"
        if not obj.question_type.is_active:
            return "🔴 Inactive Type"
        return "✅ Active"
    get_status.short_description = "Status"
    
    # Custom actions
    def duplicate_questions(self, request, queryset):
        """Duplicate selected questions"""
        count = 0
        for question in queryset:
            question.pk = None
            question.save()
            count += 1
        self.message_user(request, f"{count} question(s) duplicated successfully.")
    duplicate_questions.short_description = "Duplicate selected questions"
    
    def export_questions(self, request, queryset):
        """Export selected questions (placeholder)"""
        self.message_user(request, f"{queryset.count()} questions selected for export.")
    export_questions.short_description = "Export selected questions"

    class Media:
        """Force load custom CSS and JS for questions admin"""
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('questions/js/hotspot_coordinator.js',)



# ========== SCENARIOS ADMIN ==========
# NOTE: Scenarios admin has been moved to scenarios/admin.py for better organization.
# To manage clinical case studies, go to: /admin/scenarios/scenarios/
# The enhanced admin panel includes:
#   - Exhibit JSON templates and examples
#   - Inline question editing
#   - Help documentation for creating case studies
#   - Preview of exhibit structure
# ========== HOT SPOT MODULE ADMIN (Dedicated Interface) ==========
from .models import HotSpotQuestion
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import base64
import uuid

class HotSpotQuestionForm(forms.ModelForm):
    """
    Custom form for Hot Spot Questions that includes a virtual 'image_file' field.
    This field uploads the file to storage and saves the URL in the 'options' JSON.
    """
    image_file = forms.ImageField(
        label="Upload Hot Spot Image",
        required=False, 
        help_text="Upload the main image for the question. It will be saved and linked automatically."
    )

    class Meta:
        model = HotSpotQuestion
        fields = '__all__'
        widgets = {
            'options': forms.Textarea(attrs={'rows': 3, 'readonly': 'readonly', 'style': 'background-color: #fff3cd;'}),
            'correct_option_ids': forms.Textarea(attrs={'rows': 3, 'readonly': 'readonly', 'style': 'background-color: #d1ecf1;'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Force Question Type to HOT_SPOT and hide it
        try:
            hs_type = QuestionType.objects.get(code='HOT_SPOT')
            self.fields['question_type'].initial = hs_type
            self.fields['question_type'].widget = forms.HiddenInput()
        except QuestionType.DoesNotExist:
            pass
        
        # Make both fields visible but readonly for verification
        if 'options' in self.fields:
            self.fields['options'].required = False
            self.fields['options'].label = "Image Data (Auto-filled)"
            self.fields['options'].help_text = "The image URL is stored here automatically when you upload."
        if 'correct_option_ids' in self.fields:
            self.fields['correct_option_ids'].required = False
            self.fields['correct_option_ids'].label = "Answer Coordinates (Auto-filled)"
            self.fields['correct_option_ids'].help_text = "These coordinates are set automatically when you click the image above."

    def save(self, *args, **kwargs):
        """
        Handle the virtual image upload and update the options JSON field.
        """
        # Call the parent save with commit=False initially so we can modify the instance before saving to DB
        commit = kwargs.get('commit', True)
        instance = super().save(commit=False)
        
        # 1. Handle Image Upload
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            # Save file to media/hotspot_images/ (Standard Django Storage)
            # Use a unique name or overwrite? Standard behavior is unique.
            path = default_storage.save(f'hotspot_images/{image_file.name}', ContentFile(image_file.read()))
            image_url = default_storage.url(path)
            
            # Update options JSON
            if not isinstance(instance.options, dict):
                instance.options = {}
            instance.options['image_url'] = image_url
            
            
        if commit:
            instance.save()
            self.save_m2m() # Important for ManyToMany fields logic if any
            
        return instance
    
    def save_m2m(self):
        """Required when using commit=False in ModelForm"""
        super().save_m2m()

@admin.register(HotSpotQuestion)
class HotSpotQuestionAdmin(admin.ModelAdmin):
    """
    Dedicated Admin Interface for Hot Spot Questions.
    Hides the complexity of JSON fields and focuses on the Visual Tool.
    """
    form = HotSpotQuestionForm
    list_display = ('text', 'get_image_status', 'question_type')
    search_fields = ('text',)
    
    # Custom Fieldsets - Simplified UI for "Module" feel
    fieldsets = (
        ('Hot Spot Setup', {
            'fields': (
                'question_type', # Hidden by form logic
                'text',
                'image_file',     # Virtual field for upload
                'options',        # Hidden field (JS writes to this) - HiddenInput so no label
                'correct_option_ids',  # Hidden field (JS writes to this) - HiddenInput so no label
            ),
            'description': '<strong>Step 1:</strong> Upload an Image. <br><strong>Step 2:</strong> Click the image below (in the blue box) to set the answer.<br><strong>Step 3:</strong> Verify coordinates appear in "Answer Coordinates" field below.'
        }),
        ('Metadata', {
            'fields': ('rationale', 'difficulty_logit', 'parent_scenario', 'category_ids'),
            'classes': ('collapse',),
            'description': 'Optional extra details.'
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('questions/js/hotspot_coordinator.js',)

    def get_image_status(self, obj):
        if obj.options and isinstance(obj.options, dict) and obj.options.get('image_url'):
            return "✅ Image Present"
        return "❌ No Image"
    get_image_status.short_description = "Image Status"

    def get_queryset(self, request):
        """Only show Hot Spot questions in this list"""
        return super().get_queryset(request).filter(question_type__code__in=['HOT_SPOT', 'HOT SPOT'])
