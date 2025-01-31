from django import template

register = template.Library()

@register.filter
def has_group(user, canteen):
    """Check if a user belongs to a specific group."""
    return user.groups.filter(name=canteen).exists()
