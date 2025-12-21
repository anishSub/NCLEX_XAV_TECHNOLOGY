from django.contrib import admin
from .models import Questions

@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    # Columns: ID, Type, Truncated Text, Difficulty, and Scenario
    list_display = ('id', 'type', 'short_text', 'difficulty_logit', 'parent_scenario')
    
    # Click these to edit
    list_display_links = ('id', 'short_text')
    
    # Filters: Filter by Question Type or specific Categories
    list_filter = ('type', 'category_ids')
    
    # Search: Search the question text AND the rationale explanation
    search_fields = ('text', 'rationale')
    
    # PRO TIP: This creates a beautiful dual-pane box for selecting categories
    # Instead of holding "Ctrl+Click", you can add/remove tags easily.
    filter_horizontal = ('category_ids',)
    
    # Pagination
    list_per_page = 20

    # Custom method to shorten long questions in the list view
    def short_text(self, obj):
        return obj.text[:75] + "..." if len(obj.text) > 75 else obj.text
    short_text.short_description = "Question Text"