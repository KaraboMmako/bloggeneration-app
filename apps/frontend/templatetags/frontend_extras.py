import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def strip_heading(content, heading):
    if not content or not heading:
        return content
    stripped = content.strip()
    # Strip any leading markdown heading markers (e.g. ###, ##, #)
    import re
    stripped = re.sub(r'^#{1,6}\s*', '', stripped)
    if stripped.lower().startswith(heading.lower()):
        stripped = stripped[len(heading):].lstrip(':').strip()
    return stripped


@register.filter
def markdownify(value):
    return mark_safe(md.markdown(value or "", extensions=["extra", "nl2br"]))