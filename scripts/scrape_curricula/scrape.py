import os
import re
import requests
import time

import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

PROGRAM_TO_CURRICULUM = True


def slug(title: str) -> str:
    return re.sub(r'[^A-Za-z0-9]+', "_", title).strip("_").lower()


def get_with_backoff(url, retries=10, base_delay=0.5):
    delay = base_delay
    for _ in range(retries):
        r = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/129.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.engineering.columbia.edu/",
                "Connection": "keep-alive",
            }
        )
        if r.status_code != 429:
            r.raise_for_status()
            return r

        retry_after = r.headers.get("Retry-After")
        if retry_after:
            delay = float(retry_after)

        time.sleep(delay)
        delay *= 2

    raise requests.HTTPError("Too many 429 responses 😭")


def save_program(file_name: str, text, rewrite: bool=False) -> None:
    file_path = os.path.join("/Users/cpaynerogers/Downloads/programs", file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.isfile(file_path) and not rewrite:
        print(f"Skipping existing file: {file_name}")
        return
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(text))


with open("programs.html") as f:
    soup = BeautifulSoup(f, "html.parser")

program_links = [
    a["href"]
    for a in soup.select("a.card-program__link")
    if a.has_attr("href")
]
program_links = list(set(program_links))
program_links = [
    link
    for link in program_links
    # Some exclusion criteria
    if (
        "barnard.edu" not in link and
        "bulletin.columbia.edu" not in link
    )
]

program_links = []
for a in soup.select("a.card-program__link"):
    if not a.has_attr("href"):
        print("Skipping link with no href")
        continue

    href = a["href"]
    text = a.get_text(strip=True) or None

    # Exclusions
    if "barnard.edu" in href or "bulletin.columbia.edu" in href:
        continue

    program_links.append((href, slug(text)))
program_links = list({(href, text) for href, text in program_links})

# PROGRAMS -> CURRICULA
#
# Navigate to the program pages and get curriculum information, if possible
for base_link, title_slug in program_links:
    # Criteria for skipping:
    if (
        base_link.endswith("/apply") or
        # Because we already saved these conditions below...
        "cvn.columbia.edu" in base_link or
        not PROGRAM_TO_CURRICULUM
    ):
        print(f"Skipping link: {base_link}")
        continue

    # Get soup
    try:
        r = get_with_backoff(base_link)
    except requests.exceptions.ReadTimeout:
        print(f"Timeout getting link: {base_link}")
        continue
    except requests.exceptions.HTTPError:
        print(f"HTTP error getting link: {base_link}")
        continue
    except requests.exceptions.MissingSchema:
        print(f"Invalid link: {base_link}")
        continue
    soup = BeautifulSoup(r.text, "html.parser")

    # Handle cvn courses
    if "cvn.columbia.edu" in base_link:
        # The page we're taken to has program information
        articles = soup.find_all("article", id="main-article")
        if len(articles) != 1:
            print(base_link)
            continue
        article = articles[0]
        title = article.h1.get_text(strip=True)
        file_name = slug(title) + ".html"
        save_program(file_name, article)

    # Fall back to using trafilatura
    file_name = title_slug + ".txt"
    text = trafilatura.extract(r.text)
    save_program(file_name, text)
