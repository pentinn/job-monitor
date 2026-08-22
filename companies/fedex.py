import re
import requests
from datetime import date
from urllib.parse import urljoin
from bs4 import BeautifulSoup


FEDEX_SEARCH_URL = (
    "https://careers.fedex.com/jobs"
    "?location_type=4"
    "&keyword=software%20developer"
    "&location_name=United%20States"
)


HEADERS = {
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


TARGET_TITLE_KEYWORDS = [
    "software engineer",
    "software developer",
    "software development engineer",
    "full stack developer",
    "full-stack developer",
    "fullstack developer",
]


EXCLUDED_TITLE_KEYWORDS = [
    "manager",
    "director",
    "managing director",
    "intern",
    "Advisor"
]


def is_matching_title(title):
    """
    Check whether the FedEx job title matches
    the software engineering/development roles
    we are interested in.
    """

    title_lower = title.lower().strip()

    # Exclude management roles
    for excluded in EXCLUDED_TITLE_KEYWORDS:
        if excluded in title_lower:
            return False

    return any(
        keyword in title_lower
        for keyword in TARGET_TITLE_KEYWORDS
    )


def get_posted_date(url):
    """
    Get the exact posting date from the FedEx
    job detail page.

    Example:

    "datePosted":"2026-08-21T19:41:01.344162+00:00"
    """

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        match = re.search(
            r'"datePosted"\s*:\s*"([^"]+)"',
            response.text
        )

        if match:

            # Convert:
            # 2026-08-21T19:41:01...
            #
            # to:
            # 2026-08-21

            return match.group(1)[:10]

        return "Unknown"

    except requests.RequestException as error:

        print(
            f"Warning: Could not get posting date "
            f"for {url}: {error}"
        )

        return "Unknown"


def get_jobs():

    print("Fetching FedEx jobs...")

    response = requests.get(
        FEDEX_SEARCH_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    today = date.today().isoformat()

    print(
        f"Looking for FedEx jobs posted on {today}"
    )

    jobs = []

    seen_urls = set()

    # --------------------------------------------------
    # Find all job links
    # --------------------------------------------------

    for link in soup.find_all("a", href=True):

        href = link.get("href")

        if not href:
            continue

        if "/job/" not in href:
            continue

        url = urljoin(
            "https://careers.fedex.com",
            href
        )

        # Remove duplicate links
        if url in seen_urls:
            continue

        seen_urls.add(url)

        # --------------------------------------------------
        # Get title
        # --------------------------------------------------

        title = link.get_text(
            " ",
            strip=True
        )

        if not title:
            continue

        # --------------------------------------------------
        # Filter title
        # --------------------------------------------------

        if not is_matching_title(title):
            continue

        print(
            f"Checking posting date: {title}"
        )

        # --------------------------------------------------
        # Get posting date
        # --------------------------------------------------

        posted = get_posted_date(url)

        # --------------------------------------------------
        # Only jobs posted today
        # --------------------------------------------------

        if posted != today:
            continue

        # --------------------------------------------------
        # Extract job ID from URL
        # --------------------------------------------------

        id_match = re.search(
            r"/job/([^/?]+)$",
            url
        )

        if id_match:

            job_id = id_match.group(1)

        else:

            job_id = url

        # --------------------------------------------------
        # Add job
        # --------------------------------------------------

        jobs.append({
            "company": "FedEx",
            "id": job_id,
            "title": title,
            "location": "United States",
            "posted": posted,
            "remote": None,
            "url": url
        })

    # --------------------------------------------------
    # Remove duplicate job IDs
    # --------------------------------------------------

    unique_jobs = {}

    for job in jobs:

        unique_jobs[job["id"]] = job

    return list(
        unique_jobs.values()
    )


if __name__ == "__main__":

    jobs = get_jobs()

    print(
        f"\nFound {len(jobs)} matching FedEx jobs\n"
    )

    for job in jobs:

        print("-----------------------------")

        print(
            "ID:",
            job["id"]
        )

        print(
            "Title:",
            job["title"]
        )

        print(
            "Location:",
            job["location"]
        )

        print(
            "Posted:",
            job["posted"]
        )

        print(
            "URL:",
            job["url"]
        )