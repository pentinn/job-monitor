import json
import os

from companies.visa import get_jobs as get_visa_jobs
from companies.toast import get_jobs as get_toast_jobs
from companies.mastercard import get_jobs as get_mastercard_jobs
from notifier.email import send_email


SEEN_JOBS_FILE = "storage/seen_jobs.json"


def load_seen_jobs():
    """
    Load previously notified job IDs.
    """

    if not os.path.exists(SEEN_JOBS_FILE):
        return []

    try:
        with open(SEEN_JOBS_FILE, "r") as file:
            content = file.read().strip()

            if not content:
                return []

            return json.loads(content)

    except json.JSONDecodeError:
        print(
            "Warning: seen_jobs.json is invalid. "
            "Starting with empty history."
        )
        return []


def save_seen_jobs(job_ids):
    """
    Save notified job IDs.
    """

    os.makedirs(
        os.path.dirname(SEEN_JOBS_FILE),
        exist_ok=True
    )

    with open(SEEN_JOBS_FILE, "w") as file:
        json.dump(
            job_ids,
            file,
            indent=4
        )


def get_new_jobs(jobs):
    """
    Return only jobs that have not been notified before.
    """

    seen_jobs = set(load_seen_jobs())

    new_jobs = [
        job
        for job in jobs
        if job["id"] not in seen_jobs
    ]

    return new_jobs


def main():

    # --------------------------------
    # VISA
    # --------------------------------

    print("Checking Visa jobs...")

    visa_jobs = get_visa_jobs()

    print(
        f"Found {len(visa_jobs)} matching Visa jobs"
    )


    # --------------------------------
    # TOAST
    # --------------------------------

    print("\nChecking Toast jobs...")

    toast_jobs = get_toast_jobs()

    print(
        f"Found {len(toast_jobs)} matching Toast jobs"
    )

    # --------------------------------
    # MASTERCARD
    # --------------------------------

    print("\nChecking Mastercard jobs...")

    mastercard_jobs = get_mastercard_jobs()

    print(
        f"Found {len(mastercard_jobs)} matching Mastercard jobs"
    )

    # --------------------------------
    # COMBINE JOBS
    # --------------------------------

    jobs = (
    visa_jobs
    + toast_jobs
    + mastercard_jobs
)

    print(
        f"\nFound {len(jobs)} matching jobs in total"
    )


    # --------------------------------
    # FIND NEW JOBS
    # --------------------------------

    new_jobs = get_new_jobs(jobs)

    print(
        f"New jobs: {len(new_jobs)}"
    )


    if not new_jobs:
        print("No new jobs")
        return


    # --------------------------------
    # DISPLAY NEW JOBS
    # --------------------------------

    print("\nNew Jobs Found:\n")

    for job in new_jobs:

        print("----------------")

        print(
            "Company:",
            job["company"]
        )

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


    # --------------------------------
    # SEND EMAIL
    # --------------------------------

    # If email fails, seen_jobs.json
    # will NOT be updated.
    send_email(new_jobs)


    # --------------------------------
    # SAVE SEEN JOBS
    # --------------------------------

    # Only mark jobs as seen after
    # email succeeds.
    seen_jobs = load_seen_jobs()

    for job in new_jobs:

        if job["id"] not in seen_jobs:

            seen_jobs.append(
                job["id"]
            )


    # Save the updated list.
    save_seen_jobs(seen_jobs)

    print(
        f"Saved {len(new_jobs)} new job(s) "
        f"to {SEEN_JOBS_FILE}"
    )

    print("Email sent successfully!")


if __name__ == "__main__":
    main()