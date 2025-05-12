from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="format_result")
def format_result(result_value, normal_range):
    """
    Return the result coloured green / red depending on whether it
    falls inside the provided normal_range string (e.g. "4.0-10.0").
    """
    if result_value is None or normal_range in (None, ""):
        return result_value

    # very naive “min-max” parse
    try:
        lo, hi = [float(x) for x in normal_range.replace(" ", "").split("-")]
        val = float(result_value)
    except Exception:
        # parsing failed – just return raw value
        return result_value

    colour = "green" if lo <= val <= hi else "red"
    html = f'<span style="color:{colour}; font-weight:bold;">{val}</span>'
    return mark_safe(html)
