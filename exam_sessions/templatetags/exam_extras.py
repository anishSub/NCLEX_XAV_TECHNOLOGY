from django import template

register = template.Library()

@register.filter
def format_theta(value):
    try:
        val = float(value)
        # Adds a '+' for positive numbers, '-' for negative, rounded to 2 decimals
        return f"{val:+.2f}"
    except (ValueError, TypeError):
        return value