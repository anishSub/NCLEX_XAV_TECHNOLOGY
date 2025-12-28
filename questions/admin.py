from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
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
    
    # JSON Editor Widget - CODE MODE with full editing enabled
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget(options={
            'mode': 'code',  # Code mode with syntax highlighting
            'modes': ['code', 'tree'],  # Allow switching between code and tree view
            'mainMenuBar': True,  # Show menu bar
            'indentation': 2,  # 2-space indentation
            'escapeUnicode': False,
        })},
    }
    
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



# ========== SCENARIOS ADMIN ==========
# NOTE: Scenarios admin has been moved to scenarios/admin.py for better organization.
# To manage clinical case studies, go to: /admin/scenarios/scenarios/
# The enhanced admin panel includes:
#   - Exhibit JSON templates and examples
#   - Inline question editing
#   - Help documentation for creating case studies
#   - Preview of exhibit structure