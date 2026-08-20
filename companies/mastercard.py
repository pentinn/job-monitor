import re
import requests
from datetime import date


MASTERCARD_SEARCH_URL = (
    "https://careers.mastercard.com/us/en/search-results"
    "?keywords=software%20engineer"
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
    "director",
    "manager",
]


US_STATES = [
    "alabama",
    "alaska",
    "arizona",
    "arkansas",
    "california",
    "colorado",
    "connecticut",
    "delaware",
    "florida",
    "georgia",
    "hawaii",
    "idaho",
    "illinois",
    "indiana",
    "iowa",
    "kansas",
    "kentucky",
    "louisiana",
    "maine",
    "maryland",
    "massachusetts",
    "michigan",
    "minnesota",
    "mississippi",
    "missouri",
    "montana",
    "nebraska",
    "nevada",
    "new hampshire",
    "new jersey",
    "new mexico",
    "new york",
    "north carolina",
    "north dakota",
    "ohio",
    "oklahoma",
    "oregon",
    "pennsylvania",
    "rhode island",
    "south carolina",
    "south dakota",
    "tennessee",
    "texas",
    "utah",
    "vermont",
    "virginia",
    "washington",
    "west virginia",
    "wisconsin",
    "wyoming",
    "district of columbia",
]


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


def is_matching_title(title):
    """
    Check whether the job title matches our target roles.
    """

    title_lower = title.lower().strip()

    for excluded in EXCLUDED_TITLE_WORDS:
        if excluded in title_lower:
            return False

    return any(
        target in title_lower
        for target in TARGET_TITLES
    )


def is_us_location(location):
    """
    Determine whether a location belongs to the United States.
    """

    location_lower = location.lower()

    return any(
        state in location_lower
        for state in US_STATES
    )


def get_posted_date(url):
    """
    Get the exact posting date from Mastercard Workday.

    Example:

    "datePosted" : "2026-08-20"
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
            return match.group(1)

        return "Unknown"

    except requests.RequestException as error:

        print(
            f"Warning: Could not get posting date "
            f"for {url}: {error}"
        )

        return "Unknown"


def get_jobs():

    # --------------------------------------------------
    # Get Mastercard search page
    # --------------------------------------------------

    response = requests.get(
        MASTERCARD_SEARCH_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    # --------------------------------------------------
    # Find Mastercard Workday URLs
    # --------------------------------------------------

    pattern = (
        r'https://mastercard\.wd1\.myworkdayjobs\.com'
        r'/CorporateCareers/job/[^"\s<>]+'
    )

    urls = re.findall(
        pattern,
        response.text
    )

    # Remove duplicates
    urls = list(dict.fromkeys(urls))

    print(
        f"Found {len(urls)} Mastercard Workday URLs"
    )

    jobs = []

    # --------------------------------------------------
    # Today's date
    # --------------------------------------------------

    today = date.today().isoformat()

    print(
        f"Looking for Mastercard jobs posted on {today}"
    )

    # --------------------------------------------------
    # Process jobs
    # --------------------------------------------------

    for url in urls:

        url = url.replace(
            "/apply",
            ""
        )

        match = re.search(
            r'/job/([^/]+)/([^/]+)',
            url
        )

        if not match:
            continue

        location_slug = match.group(1)
        job_slug = match.group(2)

        # --------------------------------------------------
        # Job ID
        # --------------------------------------------------

        id_match = re.search(
            r'_R-([A-Za-z0-9-]+)',
            job_slug
        )

        if id_match:

            job_id = (
                "R-" +
                id_match.group(1)
            )

        else:

            job_id = url

        # --------------------------------------------------
        # Job title
        # --------------------------------------------------

        title_slug = re.sub(
            r'_R-[A-Za-z0-9-]+$',
            '',
            job_slug
        )

        title = title_slug.replace(
            "-",
            " "
        ).strip()

        # --------------------------------------------------
        # Filter title
        # --------------------------------------------------

        if not is_matching_title(title):
            continue

        # --------------------------------------------------
        # Location
        # --------------------------------------------------

        location = location_slug.replace(
            "-",
            " "
        )

        if not is_us_location(location):
            continue

        # --------------------------------------------------
        # Posting date
        # --------------------------------------------------

        print(
            f"Checking posting date: {title}"
        )

        posted = get_posted_date(url)

        # --------------------------------------------------
        # Only keep jobs posted today
        # --------------------------------------------------

        if posted != today:

            continue

        # --------------------------------------------------
        # Add job
        # --------------------------------------------------

        jobs.append({
            "company": "Mastercard",
            "id": job_id,
            "title": title,
            "location": location,
            "posted": posted,
            "remote": None,
            "url": url
        })

    # --------------------------------------------------
    # Remove duplicates
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
        f"\nFound {len(jobs)} Mastercard jobs "
        f"posted today\n"
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