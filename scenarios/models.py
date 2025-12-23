from django.db import models

class Scenarios(models.Model):
    """
    Parent model for NCLEX Case Studies.
    Stores clinical exhibits like Labs, Vitals, and Nurses' Notes in a JSON structure.
    """
    title = models.CharField(max_length=255)
    # Stores tabs: e.g., {"history": "...", "labs": "...", "vitals": "..."}
    exhibits = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scenarios'

    def __str__(self):
        return self.title