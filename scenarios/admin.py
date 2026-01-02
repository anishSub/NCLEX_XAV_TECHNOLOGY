from django.contrib import admin
from django import forms
from django.db import models

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
        ('Scenario Progression (For Unfolding Case Studies)', {
            'fields': ('scenario_question_number', 'clinical_judgment_function', 'exhibit_updates'),
            'classes': ('collapse',),
            'description': '''
                <strong>Configure how this question fits into the scenario:</strong><br>
                • <strong>Question Number</strong>: Set 1-6 to control delivery order<br>
                • <strong>Clinical Judgment Function</strong>: Which NCJMM function this tests<br>
                • <strong>Exhibit Updates</strong>: New/updated tabs to show (JSON format)<br><br>
                <em>Example exhibit_updates:</em><br>
                <code>{"Labs_1200": "Glucose: 180 mg/dL (↓ from 340)", "Vitals_1400": "BP: 142/84, HR: 88"}</code>
            '''
        }),
    )
    
    # Use standard Textarea to avoid blank fields on "Add Another Question"
    formfield_overrides = {
        models.JSONField: {'widget': forms.Textarea(attrs={
            'rows': 8, 
            'style': 'width: 100%; font-family: monospace;',
            'placeholder': 'Enter JSON data here...'
        })},
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Override widgets to use standard Textarea for all JSON fields
        if db_field.name in ['options', 'correct_option_ids', 'exhibit_updates']:
            kwargs['widget'] = forms.Textarea(attrs={
                'rows': 5, 
                'style': 'width: 100%; font-family: monospace;',
                'placeholder': f'Enter JSON for {db_field.name}...'
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
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
        
        # ========== NEW: Scenario Enhancement Fields ==========
        if 'scenario_question_number' in form.base_fields:
            form.base_fields['scenario_question_number'].label = 'Question Number in Scenario'
            form.base_fields['scenario_question_number'].help_text = 'Enter 1-6. Questions will be delivered in this order within the scenario.'
        
        if 'clinical_judgment_function' in form.base_fields:
            form.base_fields['clinical_judgment_function'].label = 'Clinical Judgment Function (NCJMM)'
            form.base_fields['clinical_judgment_function'].help_text = 'Select which NCLEX Clinical Judgment function this question tests'
        
        if 'exhibit_updates' in form.base_fields:
            form.base_fields['exhibit_updates'].label = 'Exhibit Updates (JSON)'
            form.base_fields['exhibit_updates'].help_text = '''
                New or updated exhibit tabs to show with this question. Leave empty if no updates needed.
                Example: {"Labs_1200": "New lab results at 12:00", "Vitals_1400": "Updated vitals at 14:00"}
            '''
            form.base_fields['exhibit_updates'].initial = {}
        
        return formset

    class Media:
        js = ('questions/js/hotspot_coordinator.js',)


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
    
    # Use fieldsets to ensure proper CSS styling (matches QuestionsAdmin structure)
    fieldsets = (
        (None, {
            'fields': ('title', 'exhibits'),
            'classes': ('wide', 'extrapretty'),
        }),
    )
    # fields = ('title', 'exhibits') removed to use fieldsets
    
    # JSON Editor Widget matching QuestionsAdmin exactly
    # Use standard Textarea to guarantee editability (Pre-fill works better with Textarea)
    formfield_overrides = {
        models.JSONField: {'widget': forms.Textarea(attrs={
            'rows': 20, 
            'style': 'width: 100%; font-family: monospace; font-size: 13px;',
            'placeholder': 'Enter JSON data here...'
        })},
    }
    
    # get_changeform_initial_data removed to allow Model default to work
    
    
    def get_changeform_initial_data(self, request):
        """Pre-fill exhibits with template for new scenarios"""
        return {
            'exhibits': {
                "History": "Patient presentation and medical history...",
                "Vitals": "BP: __, HR: __, RR: __, Temp: __, O2 Sat: __%",
                "Labs": "Relevant laboratory values...",
                "Nurses_Notes": "Time-stamped nursing observations..."
            }
        }
    
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
        """Force load custom CSS and JS for scenarios admin"""
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('questions/js/hotspot_coordinator.js',)
