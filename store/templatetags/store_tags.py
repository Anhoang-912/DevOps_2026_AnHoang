from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_vnd')
def format_vnd(value):
    """Định dạng số tiền sang chuẩn tiền tệ Việt Nam (Ví dụ: 2.350.000 ₫)."""
    if value is None or value == '':
        return "0 ₫"
    try:
        val = int(Decimal(str(value)))
        return f"{val:,}".replace(',', '.') + " ₫"
    except (ValueError, TypeError, Exception):
        return f"{value} ₫"
