from app.data.applications import APPLICATIONS


def apply_job(job, resume=None):
    application = {
        "job_id": job.get("id"),
        "company": job.get("company", "Unknown"),
        "role": job.get("title") or job.get("role", "Unknown"),
        "status": "tracked",
        "application_submitted": False,
        "apply_link": job.get("apply_link"),
        "external_application_link": job.get("apply_link"),
        "resume": resume,
    }

    APPLICATIONS.append(application)
    return application


def record_application(application):
    """Store an application workflow record for the history endpoint."""
    APPLICATIONS.append(application)
    return application


def get_applications():
    return APPLICATIONS
