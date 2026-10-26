from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='intdot')
def intdot(value):
    """Định dạng số có dấu chấm phân cách hàng nghìn (ví dụ: 3.500.000)."""
    if value is None or value == '':
        return "0"
    try:
        val = int(Decimal(str(value)))
        return f"{val:,}".replace(',', '.')
    except (ValueError, TypeError, Exception):
        return str(value)

@register.filter(name='format_vnd')
@register.filter(name='format_price')
def format_vnd(value):
    """Định dạng số tiền sang chuẩn tiền tệ Việt Nam với dấu chấm (ví dụ: 3.500.000 đ)."""
    return f"{intdot(value)} đ"
