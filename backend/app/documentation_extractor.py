from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from flask import current_app


DEFAULT_HEADINGS = ["DEFINIÇÃO", "QUEM FAZ?"]
DEFAULT_CONTENT_CLASS = "entry-content"
DEFAULT_HEADING_TAGS = ["h4"]
DEFAULT_TEXT_TAGS = ["p"]


@dataclass
class DocumentationToken:
    tag: str
    text: str


class DocumentationContentParser(HTMLParser):
    def __init__(self, content_class: str, heading_tags: list[str], text_tags: list[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.content_class = content_class
        self.heading_tags = set(heading_tags)
        self.text_tags = set(text_tags)
        self.tokens: list[DocumentationToken] = []
        self._content_depth = 0
        self._capture_tag: str | None = None
        self._capture_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()

        if self._content_depth > 0:
            self._content_depth += 1
            if self._capture_tag:
                self._capture_depth += 1

        if self._content_depth == 0 and self._has_content_class(attrs):
            self._content_depth = 1
            return

        if self._content_depth > 0 and normalized_tag in self.heading_tags | self.text_tags and not self._capture_tag:
            self._capture_tag = normalized_tag
            self._capture_depth = 1
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()

        if self._capture_tag:
            if normalized_tag == self._capture_tag:
                text = _clean_text(" ".join(self._parts))
                if text:
                    self.tokens.append(DocumentationToken(tag=self._capture_tag, text=text))
                self._capture_tag = None
                self._capture_depth = 0
                self._parts = []
            elif self._capture_depth > 0:
                self._capture_depth -= 1

        if self._content_depth > 0:
            self._content_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._capture_tag:
            self._parts.append(data)

    def _has_content_class(self, attrs: list[tuple[str, str | None]]) -> bool:
        for name, value in attrs:
            if name.lower() != "class" or not value:
                continue
            classes = {item.strip() for item in value.split()}
            if self.content_class in classes:
                return True
        return False


def extract_documentation_sections(data: dict) -> tuple[dict | None, str | None]:
    url = str(data.get("url") or "").strip()
    if not url:
        return None, "Informe a URL da documentacao."

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
        return None, "URL da documentacao invalida."

    if not _is_allowed_host(parsed_url.hostname):
        return None, "Host da documentacao nao permitido."

    headings = _list_value(data.get("headings")) or DEFAULT_HEADINGS
    content_class = str(data.get("content_class") or DEFAULT_CONTENT_CLASS).strip() or DEFAULT_CONTENT_CLASS
    heading_tags = _list_value(data.get("heading_tags")) or DEFAULT_HEADING_TAGS
    text_tags = _list_value(data.get("text_tags")) or DEFAULT_TEXT_TAGS

    html, fetch_method, error = _fetch_html(url)
    if error:
        html, fetch_method, playwright_error = _fetch_html_with_playwright(url, content_class)
        if playwright_error:
            return None, _combined_fetch_error(error, playwright_error)

    parser = DocumentationContentParser(
        content_class=content_class,
        heading_tags=[tag.lower() for tag in heading_tags],
        text_tags=[tag.lower() for tag in text_tags],
    )
    parser.feed(html)

    sections = _extract_sections(parser.tokens, headings, heading_tags)
    description = "\n\n".join(
        f"{section['heading']}\n{section['text']}"
        for section in sections
        if section["text"]
    )

    return {
        "url": url,
        "fetch_method": fetch_method,
        "content_class": content_class,
        "headings": headings,
        "sections": sections,
        "description": description,
    }, None


def _fetch_html(url: str) -> tuple[str, str, str | None]:
    request = Request(
        url,
        headers={
            "User-Agent": "SGP/0.1 documentation extractor",
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    try:
        with urlopen(request, timeout=12) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(content_type, errors="replace"), "http", None
    except HTTPError as exc:
        return "", "http", f"Nao foi possivel acessar a documentacao por HTTP. Codigo {exc.code}."
    except URLError as exc:
        reason = str(exc.reason) if exc.reason else "erro de rede"
        return "", "http", f"Nao foi possivel acessar a documentacao por HTTP. Detalhe: {reason}."
    except TimeoutError:
        return "", "http", "Tempo limite ao acessar a documentacao por HTTP."


def _fetch_html_with_playwright(url: str, content_class: str) -> tuple[str, str, str | None]:
    if not current_app.config.get("DOCUMENTATION_PLAYWRIGHT_ENABLED", True):
        return "", "playwright", "Playwright desabilitado para importacao de documentacao."

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "", "playwright", "Playwright nao esta instalado no ambiente do backend."

    timeout = int(current_app.config.get("DOCUMENTATION_PLAYWRIGHT_TIMEOUT_MS", 20000))
    proxy = str(current_app.config.get("DOCUMENTATION_PLAYWRIGHT_PROXY") or "").strip()
    launch_options: dict[str, object] = {"headless": True}

    if proxy:
        launch_options["proxy"] = {"server": proxy}

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_options)
            try:
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                try:
                    page.wait_for_selector(f".{content_class}", timeout=timeout)
                except PlaywrightTimeoutError:
                    pass
                html = page.content()
                return html, "playwright", None
            finally:
                browser.close()
    except PlaywrightTimeoutError:
        return "", "playwright", "Tempo limite ao acessar a documentacao pelo navegador."
    except PlaywrightError as exc:
        return "", "playwright", f"Nao foi possivel acessar a documentacao pelo navegador. Detalhe: {exc}."
    except Exception as exc:
        return "", "playwright", f"Nao foi possivel executar o navegador para documentacao. Detalhe: {exc}."


def _combined_fetch_error(http_error: str, playwright_error: str) -> str:
    return f"{http_error} Fallback Playwright: {playwright_error}"


def _extract_sections(
    tokens: list[DocumentationToken],
    headings: list[str],
    heading_tags: list[str],
) -> list[dict]:
    expected_headings = {_normalize_text(heading): heading for heading in headings}
    heading_tag_set = {tag.lower() for tag in heading_tags}
    sections_by_key: dict[str, dict] = {}
    current_key: str | None = None

    for token in tokens:
        token_key = _normalize_text(token.text)

        if token.tag in heading_tag_set:
            current_key = token_key if token_key in expected_headings else None
            if current_key and current_key not in sections_by_key:
                sections_by_key[current_key] = {
                    "heading": expected_headings[current_key],
                    "text": "",
                    "paragraphs": [],
                    "found": True,
                }
            continue

        if current_key and token.text:
            sections_by_key[current_key]["paragraphs"].append(token.text)

    sections = []
    for heading in headings:
        key = _normalize_text(heading)
        section = sections_by_key.get(
            key,
            {
                "heading": heading,
                "text": "",
                "paragraphs": [],
                "found": False,
            },
        )
        section["text"] = "\n\n".join(section["paragraphs"])
        sections.append(section)

    return sections


def _is_allowed_host(hostname: str) -> bool:
    hostname = hostname.lower()
    allowed_hosts = current_app.config.get("DOCUMENTATION_ALLOWED_HOSTS", [])

    for allowed_host in allowed_hosts:
        if allowed_host.startswith(".") and hostname.endswith(allowed_host):
            return True
        if hostname == allowed_host:
            return True

    return False


def _list_value(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", unescape(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text).strip().casefold()
    return text


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()
