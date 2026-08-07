import json
import os
from notifier.email import send_email
from companies.visa import get_jobs


SEEN_JOBS_FILE = "storage/seen_jobs.json"


def load_seen_jobs():
    """
    Load previously notified job IDs
    """

    if not os.path.exists(SEEN_JOBS_FILE):
        return []

    with open(SEEN_JOBS_FILE, "r") as file:
        return json.load(file)



def save_seen_jobs(job_ids):
    """
    Save notified job IDs
    """

    with open(SEEN_JOBS_FILE, "w") as file:
        json.dump(
            job_ids,
            file,
            indent=4
        )



def get_new_jobs(jobs):
    """
    Remove jobs already notified
    """

    seen_jobs = load_seen_jobs()

    new_jobs = []

    for job in jobs:

        if job["id"] not in seen_jobs:
            new_jobs.append(job)


    return new_jobs



def main():

    print("Checking Visa jobs...")


    jobs = get_jobs()


    print(
        f"Found {len(jobs)} matching jobs"
    )


    new_jobs = get_new_jobs(jobs)


    print(
        f"New jobs: {len(new_jobs)}"
    )


    if new_jobs:

        print("\nNew Jobs Found:\n")

        send_email(new_jobs)

        seen_jobs = load_seen_jobs()

        for job in new_jobs:

            print("----------------")
            print(job["title"])
            print(job["location"])
            print(job["url"])


            seen_jobs.append(job["id"])


        save_seen_jobs(seen_jobs)


    else:

        print("No new jobs")


if __name__ == "__main__":
    main()