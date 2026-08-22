import requests


VISA_API_URL = "https://visa.wd5.myworkdayjobs.com/wday/cxs/visa/Visa/jobs"


TARGET_TITLES = [
    "software engineer",
    "sw engineer",
    "senior software engineer",
    "senior sw engineer",
    "staff software engineer",
    "software development engineer",
    "sde"
]

EXCLUDED_TITLE_KEYWORDS = [
    "director",
    "senior director",
    "managing director",
    "chief",
    "vp",
    "vice president",
    "manager"
]

US_LOCATION_KEYWORDS = [
    "US",
    "United States",
    "USA"
]


def is_matching_title(title):
    """
    Check if job title matches our target roles
    """

    title = title.lower()

    if any(
        keyword in title
        for keyword in EXCLUDED_TITLE_KEYWORDS
    ):
        return False

    return any(
        keyword in title
        for keyword in TARGET_TITLES
    )

def is_us_location(location):
    """
    Check if job location is in the United States
    """

    if not location:
        return False

    location = location.upper()

    return any(
        keyword.upper() in location
        for keyword in US_LOCATION_KEYWORDS
    )


def get_jobs():
    """
    Fetch new Visa jobs posted today
    """

    all_jobs = []

    limit = 20
    offset = 0

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }


    while True:

        payload = {
            "appliedFacets": {},
            "limit": limit,
            "offset": offset,
            "searchText": "software+engineer"
        }


        response = requests.post(
            VISA_API_URL,
            json=payload,
            headers=headers
        )

        response.raise_for_status()

        data = response.json()


        for job in data.get("jobPostings", []):

            title = job.get("title", "")
            posted = job.get("postedOn", "")


            if posted != "Posted Today":
                continue


            if not is_matching_title(title):
                continue


            if not is_us_location(job.get("locationsText")):
                continue


            all_jobs.append({

                "company": "Visa",

                "id": job.get(
                    "bulletFields",
                    ["UNKNOWN"]
                )[0],

                "title": title,

                "location": job.get(
                    "locationsText"
                ),

                "posted": posted,

                "remote": job.get(
                    "remoteType"
                ),

                "url":
                    "https://visa.wd5.myworkdayjobs.com"
                    + job.get("externalPath")
            })


        offset += limit


        if offset >= data.get("total", 0):
            break


    return all_jobs


if __name__ == "__main__":

    jobs = get_jobs()


    print(
        f"\nFound {len(jobs)} new matching jobs\n"
    )


    for job in jobs:

        print("----------------------")
        print(job["title"])
        print(job["location"])
        print(job["url"])