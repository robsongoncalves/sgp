import unittest
from unittest.mock import patch

from flask import Flask
from app.documentation_extractor import extract_documentation_sections
from app.service_description import description_fields, sanitize_html


class DocumentationHtmlTests(unittest.TestCase):
    def extract(self, html, **options):
        app = Flask(__name__)
        app.config['DOCUMENTATION_ALLOWED_HOSTS'] = ['example.org']
        with app.app_context(), patch('app.documentation_extractor._fetch_html', return_value=(html, 'http', None)):
            result, error = extract_documentation_sections({
                'url': 'https://example.org/docs/page/', 'headings': ['DEFINIÇÃO', 'QUEM FAZ?'],
                'output_format': 'html', **options,
            })
        self.assertIsNone(error)
        return result

    def test_full_sections_and_boundaries(self):
        result = self.extract('''<div class="entry-content"><div>
          <h4><strong>DEFINIÇÃO</strong></h4><p>Texto <a href="../file">link</a><br>fim</p>
          <ul><li><em>Item</em></li></ul><table><tr><td colspan="2">Celula</td></tr></table>
          <img src="/image.png" alt="Imagem"><h4>OUTRO</h4><p>nao importar</p>
          </div><section><h4>QUEM FAZ?</h4><p>Equipe</p></section></div><p>fora</p>''')
        html = result['description']
        for fragment in ['<strong>', '<ul>', '<em>', '<table>', 'colspan="2"', '<br>',
                         'https://example.org/docs/file', 'https://example.org/image.png', 'Equipe']:
            self.assertIn(fragment, html)
        self.assertNotIn('nao importar', html)
        self.assertNotIn('fora', html)
        self.assertTrue(all(section['found'] for section in result['sections']))

    def test_missing_section(self):
        result = self.extract('<div class="entry-content"><h4>OUTRO</h4><p>Ignore</p></div>')
        self.assertEqual(result['description'], '')
        self.assertFalse(any(section['found'] for section in result['sections']))

    def test_empty_headings_import_full_content(self):
        result = self.extract('''<nav>Outside</nav><div class="entry-content">
          <h2>Title</h2><p>First paragraph</p><ul><li>Second item</li></ul>
          <a href="/file">File</a><script>unsafe()</script></div>''', headings=[])
        self.assertEqual(result['headings'], [])
        for value in ['Title', 'First paragraph', 'Second item', 'https://example.org/file']:
            self.assertIn(value, result['description'])
        self.assertNotIn('Outside', result['description'])
        self.assertNotIn('unsafe', result['description'])

    def test_full_content_falls_back_to_main(self):
        result = self.extract('<nav>Menu</nav><main><h1>Title</h1><p>Content</p></main>', headings=[], output_format='text')
        self.assertEqual(result['description'], 'Title Content')

    def test_legacy_text_mode(self):
        result = self.extract('<div class="entry-content"><h4>DEFINIÇÃO</h4><p>Um <b>texto</b></p></div>', output_format='text')
        self.assertEqual(result['description'], 'DEFINIÇÃO\nUm texto')

    def test_sanitization(self):
        html = sanitize_html('''<p onclick="alert(1)">Seguro<script>alert(2)</script>
          <a href="javascript:alert(3)">link</a><img src="x" onerror="alert(4)">
          <iframe src="https://example.org"></iframe><svg onload="alert(5)"></svg></p>''')
        for forbidden in ['onclick', 'onerror', 'onload', 'javascript:', '<script', '<iframe', '<svg', 'alert(']:
            self.assertNotIn(forbidden, html)
        self.assertIn('Seguro', html)

    def test_render_plain_text_and_html(self):
        self.assertEqual(description_fields('A < B & C\nOutra linha')['description_html'],
                         'A &lt; B &amp; C<br>Outra linha')
        fields = description_fields('<p>Um <strong>texto</strong></p>')
        self.assertEqual(fields['description_text'], 'Um texto')
        self.assertIn('<strong>texto</strong>', fields['description_html'])


if __name__ == '__main__':
    unittest.main()
