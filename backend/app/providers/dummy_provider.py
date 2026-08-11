from app.providers.base_provider import JobProvider
from app.data.dummy_jobs import JOBS


class DummyProvider(JobProvider):

    def search_jobs(self, query: str):

        words = query.lower().split()

        scored = []

        for job in JOBS:

            text = (
                job["title"]
                + " "
                + job["company"]
                + " "
                + job["description"]
            ).lower()

            score = 0

            for word in words:

                if word in text:
                    score += 1

            if score > 0:
                scored.append((score, job))

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [job for _, job in scored] or JOBS.copy()
