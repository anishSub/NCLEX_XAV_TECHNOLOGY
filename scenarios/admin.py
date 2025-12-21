from django.contrib import admin
from .models import Scenarios

@admin.register(Scenarios)
class ScenariosAdmin(admin.ModelAdmin):
    # Columns: Title, Date Created, and Count of Exhibits
    list_display = ('title', 'created_at', 'exhibit_count')
    
    # Click Title to edit
    list_display_links = ('title',)
    
    # Search by Title
    search_fields = ('title',)
    
    # Adds a navigation bar to browse by date (Year > Month > Day)
    date_hierarchy = 'created_at'
    
    # Pagination
    list_per_page = 20

    # Custom logic to count how many items are in the JSON 'exhibits'
    def exhibit_count(self, obj):
        # Checks if exhibits exists, then counts the keys
        return len(obj.exhibits) if obj.exhibits else 0
    
    exhibit_count.short_description = "Exhibits Count"