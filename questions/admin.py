from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from .models import Questions
from scenarios.models import Scenarios  # Assuming Scenarios is in the scenarios app

# 1. Update the Inline to use JSON Editor
class QuestionInline(admin.StackedInline):
    model = Questions
    extra = 6  # Standard NCLEX unfolding case study length
    classes = ('collapse',)
    
    # Overrides JSONField with a professional editor for your Mac M2
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    
    # Removed 'category_ids' to fix admin.E019
    fields = ('text', 'type', 'options', 'correct_option_ids', 'difficulty_logit', 'parent_scenario')

# 2. Update Scenarios Admin (The Parent)
@admin.register(Scenarios)
class ScenariosAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'exhibit_count')
    inlines = [QuestionInline] # Manages child questions directly
    
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def exhibit_count(self, obj):
        return len(obj.exhibits) if obj.exhibits else 0
    exhibit_count.short_description = "Exhibits Count"

# 3. Update Standalone Questions Admin
@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    # Fix for admin.E040: search_fields is mandatory for autocomplete
    search_fields = ('text', 'type') 
    
    list_display = ('id', 'type', 'short_text', 'difficulty_logit', 'parent_scenario')
    list_filter = ('type', 'parent_scenario')
    
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    def short_text(self, obj):
        return obj.text[:75] + "..." if len(obj.text) > 75 else obj.text
    short_text.short_description = "Question Text"