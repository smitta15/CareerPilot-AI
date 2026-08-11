"""
Company Agent - Researches company information.

Gathers company culture, tech stack, hiring process, and other relevant
information to help inform the internship decision.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.services.company_service import research_company
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import CompanyResearchError

logger = LoggerFactory.get_logger("careerpilot.agents.company")


def company_agent(state: CareerPilotState) -> Command:
    """
    Research company information.

    Gathers information about the selected company including culture,
    tech stack, interview process, and hiring expectations.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with company report and next agent

    Raises:
        CompanyResearchError: If research fails
    """
    logger.info("Starting company agent")

    try:
        # Get selected job (may be None if no matches)
        selected_job = StateValidator.get(state, "selected_job")

        if not selected_job:
            logger.warning("No selected job for company research")
            state["company_report"] = {
                "error": "No job selected",
                "overview": "",
                "tech_stack": [],
                "interview_process": "",
                "hiring_focus": "",
                "ats_keywords": []
            }
        else:
            company_name = selected_job.get("company", "Unknown")
            logger.info(f"Researching company: {company_name}")

            # Research company
            with logger.timer(f"Company research for {company_name}"):
                company_report = research_company(selected_job)

            logger.info(f"Company research completed for {company_name}")
            state["company_report"] = company_report or {}

        # Update execution plan
        if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Company agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except CompanyResearchError as e:
        logger.error(f"Company research failed: {str(e)}")
        state["error"] = str(e)
        state["company_report"] = {}
        raise

    except Exception as e:
        logger.error(f"Unexpected error in company research: {str(e)}", exc_info=True)
        state["error"] = str(e)
        state["company_report"] = {}
        raise CompanyResearchError(f"Company agent failed: {str(e)}") from e
