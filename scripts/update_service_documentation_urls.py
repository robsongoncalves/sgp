from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen


SOURCE_URL = "https://sites.unipampa.edu.br/progepe/manual-do-servidor/"
SERVICES_FILE = Path("backend/data/services.json")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def normalize(value: str) -> str:
    value = html.unescape(value).replace("\xa0", " ")
    value = value.replace("–", "-").replace("—", "-")
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def extract_links(section: str) -> list[tuple[str, str]]:
    links = []
    for match in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', section, re.I | re.S):
        url = html.unescape(match.group(1))
        text = clean_text(match.group(2))
        links.append((text, urljoin(SOURCE_URL, url)))
    return links


def documentation_link(section: str) -> str:
    li_match = re.search(r"<li[^>]*>(.*?)</li>", section, re.I | re.S)
    li_html = li_match.group(1) if li_match else ""
    li_links = extract_links(li_html)

    if li_links:
        return li_links[0][1]

    links = [
        (text, url)
        for text, url in extract_links(section)
        if "sei.unipampa.edu.br" not in url
    ]

    preferences = (
        "base de conhecimento",
        "manual do processo",
        "procedimento",
        "saiba mais",
        "orientacoes",
        "informacoes",
        "regulamento",
    )

    for preference in preferences:
        for text, url in links:
            if preference in normalize(text):
                return url

    return links[0][1] if links else ""


def service_links_from_source() -> dict[str, str]:
    page = urlopen(SOURCE_URL, timeout=30).read().decode("utf-8", "replace")
    sections = re.split(r"(?=<ul>\s*<li)", page, flags=re.I)
    links_by_name = {}

    for section in sections:
        li_match = re.search(r"<li[^>]*>(.*?)</li>", section, re.I | re.S)
        if not li_match:
            continue

        name = clean_text(li_match.group(1))
        if name:
            links_by_name[normalize(name)] = documentation_link(section)

    return links_by_name


def main() -> None:
    links_by_name = service_links_from_source()

    with SERVICES_FILE.open(encoding="utf-8") as file:
        services = json.load(file)

    unmatched = []
    for service in services:
        link = links_by_name.get(normalize(service["name"]), "")
        service["documentation_url"] = link

        if not link:
            unmatched.append(service["name"])

    with SERVICES_FILE.open("w", encoding="utf-8") as file:
        json.dump(services, file, ensure_ascii=True, indent=2)
        file.write("\n")

    print(f"Servicos atualizados: {len(services) - len(unmatched)}")
    print(f"Sem link correspondente: {len(unmatched)}")
    for name in unmatched:
        print(f"- {name}")


if __name__ == "__main__":
    main()
