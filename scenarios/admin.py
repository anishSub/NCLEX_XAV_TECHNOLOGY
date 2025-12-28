from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import Scenarios
from questions.models import Questions


# ========== QUESTION INLINE FOR SCENARIOS ==========
class QuestionInline(admin.StackedInline):
    """
    Inline form for adding questions within a scenario (Case Study).
    Use this to create multi-part unfolding case studies.
    
    This form matches the main Questions admin UI for consistency.
    """
    model = Questions
    extra = 1  # Show 1 empty form by default
    classes = ('collapse',)  # Collapsible sections
    
    # Organize fields into sections like the main Questions admin
    fieldsets = (
        ('Question Type', {
            'fields': ('question_type',),
            'description': '📝 Select the question type (MCQ, SATA, Matrix, etc.)'
        }),
        ('Question Content', {
            'fields': ('text', 'options', 'correct_option_ids', 'rationale'),
            'description': 'Enter the question text, answer choices, correct answers, and explanation'
        }),
        ('Difficulty & Classification', {
            'fields': ('difficulty_logit', 'category_ids'),
            'description': 'Set difficulty level (-3.0 to +3.0) and assign categories'
        }),
    )
    
    # JSON Editor Widget for better editing experience
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(options={
            'mode': 'code',
            'modes': ['code', 'tree'],
            'mainMenuBar': True,
            'indentation': 2,
            'escapeUnicode': False,
        })},
    }
    
    # Enable horizontal filter for categories
    filter_horizontal = ('category_ids',)
    
    def get_formset(self, request, obj=None, **kwargs):
        """Provide helpful defaults for new questions in scenario context"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Get the form class
        form = formset.form
        
        # Set helpful labels
        if 'text' in form.base_fields:
            form.base_fields['text'].label = 'Question Text'
            form.base_fields['text'].help_text = 'Enter the complete question students will see'
        
        if 'options' in form.base_fields:
            form.base_fields['options'].label = 'Answer Options (JSON)'
            form.base_fields['options'].help_text = 'Format: [{"id": "A", "text": "..."}, {"id": "B", "text": "..."}]'
            # Pre-fill with template for new questions
            form.base_fields['options'].initial = [
                {"id": "A", "text": ""},
                {"id": "B", "text": ""},
                {"id": "C", "text": ""},
                {"id": "D", "text": ""}
            ]
        
        if 'correct_option_ids' in form.base_fields:
            form.base_fields['correct_option_ids'].label = 'Correct Answer IDs'
            form.base_fields['correct_option_ids'].help_text = 'For MCQ: ["A"], For SATA: ["A", "C"]'
            form.base_fields['correct_option_ids'].initial = [""]
        
        if 'rationale' in form.base_fields:
            form.base_fields['rationale'].label = 'Rationale (Explanation)'
            form.base_fields['rationale'].help_text = 'Explain why this is the correct answer'
        
        if 'difficulty_logit' in form.base_fields:
            form.base_fields['difficulty_logit'].help_text = 'Typical range: -3.0 (easy) to +3.0 (hard), 0.0 = average'
        
        if 'category_ids' in form.base_fields:
            form.base_fields['category_ids'].help_text = 'Select all relevant content categories'
        
        return formset


# ========== SCENARIOS ADMIN ==========
@admin.register(Scenarios)
class ScenariosAdmin(admin.ModelAdmin):
    """
    Manage NCLEX Clinical Scenarios (Case Studies) with embedded questions.
    Uses the same clean layout as Questions admin.
    """
    
    list_display = ('title', 'created_at', 'exhibit_count', 'question_count')
    list_filter = ('created_at',)
    search_fields = ('title',)
    inlines = [QuestionInline]
    
    # SIMPLIFIED: Just list the fields, no complex fieldsets
    # This matches how Questions admin works
    fields = ('title', 'exhibits')
    
    # JSON Editor Widget with enhanced options
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(options={
            'mode': 'code',  # Code mode for better editing
            'modes': ['code', 'tree', 'view'],  # Allow switching views
            'mainMenuBar': True,
            'indentation': 2,
            'escapeUnicode': False,
        })},
    }
    
    def get_form(self, request, obj=None, **kwargs):
        """Pre-fill exhibits with template for new scenarios"""
        form = super().get_form(request, obj, **kwargs)
        
        # Only pre-fill for new scenarios (not editing existing)
        if not obj and 'exhibits' in form.base_fields:
            form.base_fields['exhibits'].initial = {
                "History": "Patient presentation and medical history...",
                "Vitals": "BP: __, HR: __, RR: __, Temp: __, O2 Sat: __%",
                "Labs": "Relevant laboratory values...",
                "Nurses_Notes": "Time-stamped nursing observations..."
            }
        
        return form
    
    def exhibit_count(self, obj):
        """Display number of exhibit tabs"""
        count = len(obj.exhibits) if obj.exhibits else 0
        if count == 0:
            return "⚠️ No exhibits"
        return f"{count} tab{'s' if count != 1 else ''}"
    exhibit_count.short_description = "Exhibits"
    
    def question_count(self, obj):
        """Display number of linked questions"""
        count = obj.questions.count()
        if count == 0:
            return "⚠️ No questions"
        return f"{count} question{'s' if count != 1 else ''}"
    question_count.short_description = "Questions"
    
    # Custom admin actions
    actions = ['duplicate_scenario']
    
    def duplicate_scenario(self, request, queryset):
        """Duplicate selected scenarios (without questions)"""
        count = 0
        for scenario in queryset:
            original_title = scenario.title
            scenario.pk = None  # Create new instance
            scenario.title = f"{original_title} (Copy)"
            scenario.save()
            count += 1
        
        self.message_user(
            request, 
            f"{count} scenario(s) duplicated successfully. "
            "Note: Questions were NOT copied - add them manually."
        )
    duplicate_scenario.short_description = "Duplicate selected scenarios"
    
    class Media:
        """Force load custom CSS for scenarios admin"""
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
