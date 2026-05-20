from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_attribute(queryset, attr):
    return sum(getattr(item, attr, Decimal(0)) for item in queryset)

@register.filter
def sum_remaining(queryset):
    return sum(item.remaining for item in queryset)
