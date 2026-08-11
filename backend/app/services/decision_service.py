from app.services.models import agent_llm
from app.models.decision_model import Decision
from app.utils.retry import retry_llm

try:
    structured_llm = agent_llm.with_structured_output(Decision) if agent_llm else None
except Exception:
    structured_llm = None


def make_decision(state):
    selected_job = state.get("selected_job") or {}
    profile = state.get("profile") or {}
    match_score = int(state.get("match_score") or 0)
    company_report = state.get("company_report") or {}
    skill_gap = state.get("skill_gap") or {}
    missing_skills = []

    if isinstance(skill_gap, dict):
        missing_skills = skill_gap.get("missing_skills") or []
        if isinstance(missing_skills, str):
            missing_skills = [missing_skills]
    elif isinstance(skill_gap, str):
        missing_skills = [skill_gap]

    if not selected_job:
        return {
            "decision": "reject",
            "confidence": 100,
            "reason": "No job was selected for evaluation.",
            "recommendation": "Do not proceed without a selected opportunity.",
            "summary": "No selected job was available.",
            "strengths": [],
            "weaknesses": ["No job context was available for decision-making."],
            "next_steps": ["Choose a job from the search results before applying."],
        }

    confident_apply = match_score >= 70 and len(missing_skills) <= 2
    needs_input = match_score >= 50 and len(missing_skills) > 2
    decision = "apply" if confident_apply else "ask_user" if needs_input else "reject"

    prompt = f"""
You are an AI Career Advisor.

Candidate Profile:
{profile}

Selected Job:
{selected_job}

Match Score:
{match_score}

Company Research:
{company_report}

Skill Gap:
{skill_gap}

Previous Applications:
{state.get("applications", [])}

Decide ONE of:

- apply
- reject
- ask_user

Return a short but useful recommendation for the user.
"""

    if structured_llm is not None:
        try:
            result = retry_llm(lambda: structured_llm.invoke(prompt))
            payload = result.model_dump()
            if payload.get("decision"):
                payload["recommendation"] = payload.get("recommendation") or payload.get("summary") or payload.get("reason")
                return payload
        except Exception:
            pass

    recommendation_map = {
        "apply": "Strong fit for this role. A tracked application is reasonable.",
        "ask_user": "This role is interesting but requires a final check before tracking an application.",
        "reject": "The role is a poor fit based on current skills and match score.",
    }
    strength_text = [
        f"Match score is {match_score}%.",
        f"The role aligns with {selected_job.get('title', 'the target role')}.",
    ]
    weakness_text = [
        f"Missing skills: {', '.join(missing_skills) if missing_skills else 'No major gaps identified.'}",
    ]
    next_steps = [
        "Review the company and role fit before tracking the application.",
    ]
    if missing_skills:
        next_steps.append(f"Build familiarity with: {', '.join(missing_skills[:3])}.")

    return {
        "decision": decision,
        "confidence": max(55, min(98, match_score + (15 if decision == 'apply' else 5))),
        "reason": f"Match score {match_score}% and {len(missing_skills)} missing skills inform this recommendation.",
        "recommendation": recommendation_map[decision],
        "summary": recommendation_map[decision],
        "strengths": strength_text,
        "weaknesses": weakness_text,
        "next_steps": next_steps,
    }