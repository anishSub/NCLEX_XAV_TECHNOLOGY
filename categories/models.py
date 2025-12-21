from django.db import models

class Categories(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name