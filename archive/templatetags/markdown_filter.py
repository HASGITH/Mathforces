from django import template
import markdown
import bleach

register = template.Library()

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'ul', 'ol', 'li', 'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'sup', 'sub'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
    '*': []
}

@register.filter(name='markdown')
def markdown_to_html(text):
    """Преобразует Markdown в HTML и очищает опасное содержимое."""
    if not text:
        return ''
    
    # Преобразуем Markdown в HTML
    html = markdown.markdown(
        text,
        extensions=['tables', 'fenced_code', 'codehilite'],
        extension_configs={
            'codehilite': {'use_pygments': False}
        }
    )
    
    # Очищаем HTML от опасного контента
    cleaned_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return cleaned_html
