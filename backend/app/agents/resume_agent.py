"""
Resume Agent - Tailors resume for the job.

Customizes the master resume based on job requirements, company culture,
and identified skill gaps.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.services.resume_service import tailor_resume
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import ResumeTailoringError

logger = LoggerFactory.get_logger("careerpilot.agents.resume")


def resume_agent(state: CareerPilotState) -> Command:
    """
    Tailor resume for the job.

    Customizes the master resume based on job requirements, company culture,
    and identified skill gaps to maximize ATS compatibility and impact.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with tailored resume and next agent

    Raises:
        ResumeTailoringError: If tailoring fails
    """
    logger.info("Starting resume agent")

    try:
        # Get required context
        selected_job = StateValidator.get(state, "selected_job")
        profile = StateValidator.get_dict(state, "profile", {})

        if not selected_job:
            logger.warning("No selected job for resume tailoring")
            state["tailored_resume"] = "# Resume\n\nNo job selected for tailoring"
        else:
            job_title = selected_job.get("title", "Unknown")
            logger.info(f"Tailoring resume for {job_title}")

            # Tailor resume
            with logger.timer("Resume tailoring"):
                tailored = tailor_resume(selected_job, profile)

            logger.info("Resume tailored successfully")
            state["tailored_resume"] = tailored or ""

        # Update execution plan
        if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Resume agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except ResumeTailoringError as e:
        logger.error(f"Resume tailoring failed: {str(e)}")
        state["error"] = str(e)
        state["tailored_resume"] = ""
        raise

    except Exception as e:
        logger.error(f"Unexpected error in resume tailoring: {str(e)}", exc_info=True)
        state["error"] = str(e)
        state["tailored_resume"] = ""
        raise ResumeTailoringError(f"Resume agent failed: {str(e)}") from e
