"""
Skill Gap Agent - Identifies missing skills.

Compares user skills with job requirements and company expectations
to identify skill gaps that should be addressed.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.services.skill_gap_service import analyze_skill_gap
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import SkillGapAnalysisError

logger = LoggerFactory.get_logger("careerpilot.agents.skill_gap")


def skill_gap_agent(state: CareerPilotState) -> Command:
    """
    Analyze skill gaps.

    Compares user profile skills with job requirements and company
    expectations to identify areas for improvement.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with skill gap analysis and next agent

    Raises:
        SkillGapAnalysisError: If analysis fails
    """
    logger.info("Starting skill gap agent")

    try:
        # Get required context
        selected_job = StateValidator.get(state, "selected_job")
        profile = StateValidator.get_dict(state, "profile", {})

        if not selected_job:
            logger.warning("No selected job for skill gap analysis")
            state["skill_gap"] = {"missing_skills": [], "analysis": "No job selected"}
        else:
            job_title = selected_job.get("title", "Unknown")
            logger.info(f"Analyzing skill gap for {job_title}")

            # Analyze gaps
            with logger.timer("Skill gap analysis"):
                skill_gap = analyze_skill_gap(profile, selected_job)

            logger.info("Skill gap analysis completed")
            state["skill_gap"] = skill_gap or {}

        # Update execution plan
        if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Skill gap agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except SkillGapAnalysisError as e:
        logger.error(f"Skill gap analysis failed: {str(e)}")
        state["error"] = str(e)
        state["skill_gap"] = {}
        raise

    except Exception as e:
        logger.error(f"Unexpected error in skill gap analysis: {str(e)}", exc_info=True)
        state["error"] = str(e)
        state["skill_gap"] = {}
        raise SkillGapAnalysisError(f"Skill gap agent failed: {str(e)}") from e
