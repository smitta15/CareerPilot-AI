"""
Matching Agent - Ranks and selects the best job.

Scores each job opportunity based on profile match and selects
the highest-ranked option for further analysis.
"""

from langgraph.types import Command

from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent

from app.services.matching_service import rank_jobs
from app.services.scoring_service import deterministic_score

from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import MatchingError

logger = LoggerFactory.get_logger("careerpilot.agents.matching")


def matching_agent(state: CareerPilotState) -> Command:
    """
    Rank jobs and select the best match.

    Scores each job opportunity against the user profile and selects
    the highest-ranked option for further analysis.
    """

    logger.info("Starting matching agent")

    try:

        jobs = StateValidator.get_list(state, "opportunities", [])
        profile = StateValidator.get_dict(state, "profile", {})

        logger.info(f"Matching {len(jobs)} jobs against profile")

        if not jobs:

            logger.warning("No opportunities to match; setting defaults")

            state["selected_job"] = None
            state["shortlisted_jobs"] = []
            state["match_score"] = 0
            state["match_reason"] = "No jobs found"

        else:

            # ---------------------------------------------------
            # STEP 1: Deterministic Scoring
            # ---------------------------------------------------

            for job in jobs:

                job["base_score"] = deterministic_score(
                    state["user_query"],
                    profile,
                    job
                )

            jobs.sort(
                key=lambda job: job.get("base_score", 0),
                reverse=True
            )

            logger.info("Top deterministic scores:")

            for job in jobs[:5]:

                logger.info(
                    f"{job['title']} -> {job['base_score']}"
                )

            # ---------------------------------------------------
            # STEP 2: Send only Top-5 jobs to LLM
            # ---------------------------------------------------

            top_jobs = jobs[:5]

            with logger.timer("Job ranking"):

                rankings = rank_jobs(
                    profile,
                    state["user_query"],
                    top_jobs
                )

            logger.info(f"Ranked {len(rankings)} jobs")

            # ---------------------------------------------------
            # STEP 3: Combine LLM + Deterministic Score
            # ---------------------------------------------------

            for ranking in rankings:

                if ranking.index >= len(top_jobs):
                    continue

                job = top_jobs[ranking.index]

                llm_score = ranking.score
                base_score = job["base_score"]

                job["match_score"] = round(
                    (0.4 * base_score) +
                    (0.6 * llm_score),
                    2
                )

                job["match_reason"] = ranking.reason

            # Remaining jobs use deterministic score only

            for job in jobs[5:]:

                job["match_score"] = job["base_score"]
                job["match_reason"] = "Ranked using deterministic scoring."

            # ---------------------------------------------------
            # STEP 4: Final Ranking
            # ---------------------------------------------------

            jobs.sort(
                key=lambda job: job.get("match_score", 0),
                reverse=True
            )

            state["shortlisted_jobs"] = jobs
            state["selected_job"] = jobs[0]
            state["match_score"] = jobs[0]["match_score"]
            state["match_reason"] = jobs[0]["match_reason"]

            logger.info(
                f"Selected job: {jobs[0]['title']} | "
                f"Base Score={jobs[0]['base_score']} | "
                f"Final Score={jobs[0]['match_score']}"
            )

        # ---------------------------------------------------
        # Update execution plan
        # ---------------------------------------------------

        StateValidator.validate_required_fields(
            state,
            ["execution_plan"]
        )

        if (
            state["execution_plan"]
            and len(state["execution_plan"]) > state.get("current_step", 0)
        ):

            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Matching agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except MatchingError as e:

        logger.error(f"Matching failed: {str(e)}")

        state["error"] = str(e)
        state["selected_job"] = None
        state["match_score"] = 0

        raise

    except Exception as e:

        logger.error(
            f"Unexpected error in matching: {str(e)}",
            exc_info=True
        )

        state["error"] = str(e)
        state["selected_job"] = None

        raise MatchingError(
            f"Matching agent failed: {str(e)}"
        ) from e