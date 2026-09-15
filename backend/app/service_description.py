"""Safe HTML rendering shared by the admin API and the public catalog."""
import re
from html import escape
from urllib.parse import urljoin

import bleach
from bs4 import BeautifulSoup

TAGS = frozenset('p br hr h1 h2 h3 h4 h5 h6 a strong b em i u s del sub sup ul ol li dl dt dd blockquote pre code table thead tbody tfoot tr th td caption div span img figure figcaption'.split())


def sanitize_html(value: str, base_url: str = '') -> str:
    soup = BeautifulSoup(value, 'html.parser')
    for element in soup.find_all(['script', 'style', 'iframe', 'object', 'embed', 'template']):
        element.decompose()
    if base_url:
        for element in soup.find_all(True):
            for attribute in ('href', 'src'):
                if element.has_attr(attribute):
                    element[attribute] = urljoin(base_url, element[attribute])
    return bleach.clean(
        str(soup), tags=TAGS,
        attributes={'*': ['title'], 'a': ['href'], 'img': ['src', 'alt', 'width', 'height'],
                    'td': ['colspan', 'rowspan'], 'th': ['colspan', 'rowspan', 'scope'],
                    'ol': ['start', 'reversed'], 'li': ['value']},
        protocols={'http', 'https', 'mailto', 'tel'}, strip=True,
    ).strip()


def description_fields(value: str) -> dict:
    value = value or ''
    is_html = bool(re.search(r'</?[a-zA-Z][^>]*>', value))
    html = sanitize_html(value) if is_html else '<br>'.join(escape(value).splitlines())
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True) if is_html else value
    return {'description_html': html, 'description_text': text}
