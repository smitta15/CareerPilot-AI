from app.providers.dummy_provider import DummyProvider

providers = [
    DummyProvider(),
]


def search_jobs(query: str):

    jobs = []

    for provider in providers:
        jobs.extend(provider.search_jobs(query))

    return jobs