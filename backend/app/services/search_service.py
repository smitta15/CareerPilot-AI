from app.services.job_api_service import search_jobs


def remove_duplicates(jobs):

    unique = []
    seen = set()

    for job in jobs:

        key = (
            str(job.get("title", "")).lower(),
            str(job.get("company", "")).lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(job)

    return unique


def filter_invalid_jobs(jobs):

    valid = []

    for job in jobs:

        if not job.get("title"):
            continue

        if not job.get("company"):
            continue

        if not job.get("description"):
            continue

        valid.append(job)

    return valid


def search_opportunities(query):

    jobs = search_jobs(query)

    jobs = filter_invalid_jobs(jobs)

    jobs = remove_duplicates(jobs)

    return jobs
