import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


TOAST_SEARCH_URL = (
    "https://careers.toasttab.com/jobs/search"
    "?page=1"
    "&country_codes%5B%5D=US"
    "&query=software+engineer"
)


TARGET_TITLES = [
    "software engineer",
    "sw engineer",
    "senior software engineer",
    "senior sw engineer",
    "staff software engineer",
    "staff sw engineer",
]


EXCLUDED_TITLE_WORDS = [
    "principal",
]


def is_matching_title(title):
    """
    Check whether the job title matches our target roles.
    """

    title_lower = title.lower().strip()

    # Exclude Principal / Senior Principal roles
    for excluded in EXCLUDED_TITLE_WORDS:
        if excluded in title_lower:
            return False

    # Match desired software engineering titles
    return any(
        target in title_lower
        for target in TARGET_TITLES
    )


def get_jobs():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    response = requests.get(
        TOAST_SEARCH_URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    jobs = []

    for link in soup.find_all("a", href=True):

        href = link["href"]

        if "/jobs/" not in href:
            continue

        title = link.get_text(
            " ",
            strip=True
        )

        if not title:
            continue

        if not is_matching_title(title):
            continue

        url = urljoin(
            "https://careers.toasttab.com",
            href
        )

        jobs.append({
            "company": "Toast",
            "id": url,
            "title": title,
            "location": "United States",
            "posted": "Unknown",
            "remote": None,
            "url": url
        })

    # Remove duplicate jobs
    unique_jobs = {}

    for job in jobs:
        unique_jobs[job["id"]] = job

    return list(unique_jobs.values())


if __name__ == "__main__":

    jobs = get_jobs()

    print(
        f"Found {len(jobs)} matching Toast jobs"
    )

    for job in jobs:

        print("-----------------------------")

        print("Title:", job["title"])
        print("Location:", job["location"])
        print("URL:", job["url"])
        print("ID:", job["id"])