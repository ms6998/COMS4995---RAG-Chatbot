import requests
import time
from difflib import SequenceMatcher
from pprint import pprint
from urllib.parse import quote


def get_with_backoff(url, retries=10, base_delay=0.5):
    delay = base_delay
    for _ in range(retries):
        r = requests.get(url, timeout=5)
        if r.status_code != 429:
            r.raise_for_status()
            return r.json()

        retry_after = r.headers.get("Retry-After")
        if retry_after:
            delay = float(retry_after)

        time.sleep(delay)
        delay *= 2

    raise requests.HTTPError("Too many 429 responses 😭")


def string_similarity(a: str, b: str):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def name_matches(name: str, results: list, threshold: float = 0.9):
    """
    Assumes space-delimiting and first result is most important
    """
    PROF = "professor_header"
    search_name = name.split(" ")[0] + " " + name.split(" ")[-1]
    result_name = results[0][PROF]["first_name"] + " " + results[0][PROF]["last_name"]
    return string_similarity(search_name, result_name) >= threshold


def get_professor_ids(name: str, debug: bool=False):
    """
    Uses the Culpa API to get professor IDs. The logic can probably
    be cleaned up
    """
    BASE_URL = "https://culpa.info/api/search/search?queryString="
    PROF = "professor_header"
    REL = "relevance"
    ID = "professor_id"
    TOL = 0.05

    # Search with an exponential backoff to avoid HTTP 429
    # killing the search
    results = get_with_backoff(BASE_URL + quote(name))

    # Remove all results except professors
    results = [r for r in results if PROF in r.keys()]

    # We may not get a result
    if len(results) == 0:
        if debug:
            print(f"No results for '{name}'")
        return None

    # The first result is "most relevant" - but, does the name match?
    if not name_matches(name, results):
        if debug:
            print(f"Name does not match for '{name}'")
        return None

    # We may have a perfect match?
    if len(results) == 1:
        if debug:
            print(f"Just one result for '{name}':")
            pprint(results)
        return [results[0][PROF][ID]]

    # We may need to consider how relevant our matches are
    # Is this a good way?
    total_relevance = 0
    for r in results:
        total_relevance += r[REL]
    for r in results:
        if r[REL] / total_relevance > 0.5:
            return [r[PROF][ID]]

    # Or is this a good way?
    if results[0][REL] > 1.25 * results[1][REL]:
        return [results[0][PROF][ID]]

    # We may have repeat professor entries
    # Not sure if or how to deduplicate them
    past_match = None
    professor_ids = []
    for i, r in enumerate(results):
        # The first professor match
        if not professor_ids:
            past_match = r
            professor_ids.append(r[PROF][ID])

        # Subsequent, very similar matches
        if (
            past_match and
            professor_ids and
            name_matches(name, [r]) and
            abs(past_match[REL] / r[REL] - 1.0) < TOL
        ):
            professor_ids.append(r[PROF][ID])
    # If this worked, return it
    if len(professor_ids) > 1:
        return professor_ids

    # Works well enough
    print(f"Missed parsing results for {name}")
    return None


def get_professor_rating(professor_id: str, debug: bool=False):
    url = f"https://culpa.info/api/professor_page/card/{professor_id}"
    r = get_with_backoff(url)
    return r["professor_summary"]["avg_rating"]
