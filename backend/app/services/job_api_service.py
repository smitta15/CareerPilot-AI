
import os
import requests
from dotenv import load_dotenv

from app.services.job_parser_service import extract_skills
from app.providers.provider_manager import search_jobs as search_provider_jobs

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"


def normalize_job(job):
    description = job.get("description") or ""
    company_info = job.get("company") or {}
    location_info = job.get("location") or {}

    return {
        "id": str(job.get("id", "")),
        "title": job.get("title", ""),
        "company": company_info.get("display_name") if isinstance(company_info, dict) else str(company_info or "Unknown"),
        "location": location_info.get("display_name") if isinstance(location_info, dict) else str(location_info or "Remote"),
        "description": description,
        "employment_type": job.get("contract_type") or job.get("employment_type") or "",
        "apply_link": job.get("redirect_url") or job.get("apply_link") or "",
        "skills": extract_skills(description),
    }


def search_jobs(search_request):
    fallback_jobs = search_provider_jobs(search_request.role)

    if not APP_ID or not APP_KEY:
        return fallback_jobs

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 20,
        "what": search_request.role,
    }

    if search_request.skills:
        params["what_and"] = " ".join(search_request.skills)

    if search_request.location:
        params["where"] = search_request.location

    try:
        response = requests.get(BASE_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        jobs = [normalize_job(job) for job in data.get("results", [])]
        if jobs:
            return jobs
    except Exception:
        pass

    return fallback_jobs
