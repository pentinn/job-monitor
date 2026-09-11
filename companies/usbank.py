import requests

US_BANK_API_URL = (
    "https://usbank.wd1.myworkdayjobs.com/"
    "wday/cxs/usbank/US_Bank_Careers/jobs"
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
    "full stack engineer",
    "full stack developer",
]

EXCLUDED_TITLE_KEYWORDS = [
    "director",
    "manager",
    "chief",
    "vp",
    "vice president",
    "principal",
]

US_LOCATION_KEYWORDS = [
    "-CA/",
    "-TX/",
    "-MN/",
    "-IL/",
    "-WI/",
    "-AZ/",
    "-CO/",
    "-OH/",
    "-MO/",
    "-NJ/",
    "-NY/",
    "-NC/",
    "-VA/",
    "-MD/",
    "-FL/",
    "-GA/",
    "-WA/",
    "-OR/",
    "-UT/",
    "-IA/",
    "-NE/",
    "-KS/",
    "-TN/",
    "-PA/",
    "-MA/",
    "-CT/",
    "-MI/",
    "-IN/",
    "-KY/",
    "-SC/",
    "-AL/",
    "-OK/",
    "-AR/",
    "-LA/",
    "-NV/",
    "-ID/",
    "-MT/",
    "-ND/",
    "-SD/",
    "-WY/",
    "-NM/",
    "-MS/",
    "-ME/",
    "-NH/",
    "-RI/",
    "-VT/",
    "-WV/",
    "-DE/",
    "-DC/",
]


def is_matching_title(title):
    title_lower = title.lower()

    if any(
        keyword in title_lower
        for keyword in EXCLUDED_TITLE_KEYWORDS
    ):
        return False

    return any(
        keyword in title_lower
        for keyword in TARGET_TITLES
    )


def is_us_location(external_path):
    if not external_path:
        return False

    return any(
        keyword in external_path.upper()
        for keyword in US_LOCATION_KEYWORDS
    )


def get_jobs():
    all_jobs = []
    limit = 20
    offset = 0

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    while True:
        payload = {
            "appliedFacets": {},
            "limit": limit,
            "offset": offset,
            "searchText": "software engineer",
        }

        response = requests.post(
            US_BANK_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        for job in data.get("jobPostings", []):
            title = job.get("title", "")
            posted = job.get("postedOn", "")
            external_path = job.get("externalPath", "")

            if posted != "Posted Today":
                continue

            if not is_matching_title(title):
                continue

            if not is_us_location(external_path):
                continue

            job_id = job.get("bulletFields", ["UNKNOWN"])[0]

            all_jobs.append({
                "company": "U.S. Bank",
                "id": job_id,
                "title": title,
                "location": job.get("locationsText"),
                "posted": posted,
                "remote": job.get("remoteType"),
                "url": (
                    "https://usbank.wd1.myworkdayjobs.com"
                    + external_path
                ),
            })

        offset += limit

        if offset >= data.get("total", 0):
            break

    return all_jobs


if __name__ == "__main__":
    jobs = get_jobs()

    print(f"\nFound {len(jobs)} matching U.S. Bank jobs\n")

    for job in jobs:
        print("----------------------")
        print("Title:", job["title"])
        print("Location:", job["location"])
        print("Posted:", job["posted"])
        print("URL:", job["url"])