import re


def normalize(text: str) -> set[str]:
    """
    Convert text into normalized tokens.
    """

    if not text:
        return set()

    words = re.findall(r"[a-zA-Z0-9+#.]+", text.lower())

    stop_words = {
        "the", "and", "of", "for", "to", "with",
        "a", "an", "in", "on", "at", "by",
        "job", "role", "position"
    }

    return {
        word
        for word in words
        if word not in stop_words
    }


def title_score(user_query: str, job_title: str) -> int:
    """
    Generic role similarity score.
    Works for ANY job profile.
    """

    query_words = normalize(user_query)
    title_words = normalize(job_title)

    if not query_words or not title_words:
        return 0

    common = query_words.intersection(title_words)

    similarity = len(common) / len(query_words)

    return round(similarity * 40)


def skill_score(candidate_skills, job_skills) -> int:
    """
    Score based on common skills.
    """

    if not candidate_skills or not job_skills:
        return 0

    candidate = {
        skill.lower()
        for skill in candidate_skills
    }

    required = {
        skill.lower()
        for skill in job_skills
    }

    common = candidate.intersection(required)

    if not common:
        return 0

    score = min(30, len(common) * 5)

    return score


def deterministic_score(user_query, profile, job):
    """
    Overall deterministic score.
    """

    score = 0

    score += title_score(
        user_query,
        job["title"]
    )

    score += skill_score(
        profile["skills"],
        job["skills"]
    )

    return score