from django.db import models

# Function kept to prevent migration verify errors
def get_default_exhibits():
    return {
        "History": "Patient presentation and medical history...",
        "Vitals": "BP: __, HR: __, RR: __, Temp: __, O2 Sat: __%",
        "Labs": "Relevant laboratory values...",
        "Nurses_Notes": "Time-stamped nursing observations..."
    }

class Scenarios(models.Model):
    """
    Parent model for NCLEX Case Studies.
    Stores clinical exhibits like Labs, Vitals, and Nurses' Notes in a JSON structure.
    """
    title = models.CharField(max_length=255)
    # Stores tabs: e.g., {"history": "...", "labs": "...", "vitals": "..."}
    exhibits = models.JSONField(default=get_default_exhibits, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scenarios'

    def __str__(self):
        return self.title