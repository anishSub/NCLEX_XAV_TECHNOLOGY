from django.contrib import admin
from .models import Categories

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = ('name', 'type', 'parent_category', 'id')
    
    # Clickable links to edit the row (usually the first column)
    list_display_links = ('name',)
    
    # Add a filter sidebar on the right
    list_filter = ('type', 'parent_category')
    
    # Add a search box at the top
    search_fields = ('name', 'type')
    
    # Pagination (useful if you have hundreds of categories)
    list_per_page = 25
    
    # Sort order (alphabetical by name)
    ordering = ('name',)

    # Logic to show "No Parent" nicely in the UI
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent_category')