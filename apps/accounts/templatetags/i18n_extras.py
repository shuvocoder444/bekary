from django import template
from config.translations import translate_text

register = template.Library()


@register.filter(name='trans_bn')
def trans_bn(text, current_lang='bn'):
    """
    Template filter usage:
    {{ "Dashboard"|trans_bn:current_lang }}
    """
    if not text:
        return ""
    return translate_text(str(text), lang=current_lang)


@register.simple_tag(takes_context=True)
def t(context, text):
    """
    Simple tag usage:
    {% t "Dashboard" %}
    Automatically picks 'current_lang' from the template context.
    """
    current_lang = context.get('current_lang', 'en')
    return translate_text(str(text), lang=current_lang)
