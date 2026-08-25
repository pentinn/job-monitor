import json
import re
from datetime import datetime, date

import requests


ULINE_URL = (
    "https://www.uline.jobs/JobSearchResults"
    "?culture=en&searchType=1&search=Software+Developer"
    "&radius=50&jr_id=external_1785857638816_99"
)

TARGET_TITLES = [
    "software engineer",
    "sw engineer",
    "senior software engineer",
    "senior sw engineer",
    "staff software engineer",
    "lead software engineer",
    "software development engineer",
    "sde",
    "software developer",
    "senior software developer",
    "sr. software developer",
    "staff software developer",
    "lead software developer",
    "full stack developer",
    "full-stack developer",
    "fullstack developer",
]

EXCLUDED_TITLE_KEYWORDS = [
    "director",
    "chief",
    "vp",
    "vice president",
    "manager",
]


def is_matching_title(title):
    title = title.lower().strip()

    if any(
        keyword in title
        for keyword in EXCLUDED_TITLE_KEYWORDS
    ):
        return False

    return any(
        keyword in title
        for keyword in TARGET_TITLES
    )


def get_posted_date(timestamp):
    """
    Convert Uline /Date(milliseconds)/ format to YYYY-MM-DD.
    """

    match = re.search(
        r"/Date\((\d+)",
        timestamp
    )

    if not match:
        return None

    milliseconds = int(match.group(1))

    return datetime.fromtimestamp(
        milliseconds / 1000
    ).date().isoformat()


def get_jobs():
    """
    Fetch Uline jobs posted today.
    """

    response = requests.get(
        ULINE_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.uline.jobs/",
        },
        timeout=30
    )

    response.raise_for_status()

    match = re.search(
        r"var existingJobResults = (\[.*?\]);",
        response.text,
        re.DOTALL
    )

    if not match:
        print("Could not find Uline job data.")
        return []

    jobs_data = json.loads(match.group(1))

    today = date.today().isoformat()

    jobs = []

    for job in jobs_data:

        title = job.get("JobTitle", "")
        posted = get_posted_date(
            job.get("JobPostedDate", "")
        )

        if not is_matching_title(title):
            continue

        if posted != today:
            continue

        job_id = job.get("JobId")

        title_param = job.get(
            "GetJobTitleParam",
            ""
        )

        url = (
            "https://www.uline.jobs/"
            + title_param
            + "/job/"
            + job_id
        )

        jobs.append({
            "company": "Uline",
            "id": job_id,
            "title": title,
            "location": job.get("UlineLocation"),
            "posted": posted,
            "remote": None,
            "url": url
        })

    return jobs


if __name__ == "__main__":

    jobs = get_jobs()

    print(
        f"\nFound {len(jobs)} matching Uline jobs\n"
    )

    for job in jobs:

        print("----------------------")

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