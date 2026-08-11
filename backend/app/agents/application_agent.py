"""
Application Agent - Submits job application.

Submits the user's application to the selected job after approval.
Records the application for tracking and history.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import ApplicationError
from app.services.application_service import apply_job, record_application
from datetime import datetime

logger = LoggerFactory.get_logger("careerpilot.agents.application")


def application_agent(state: CareerPilotState) -> Command:
    """
    Submit job application.

    Submits the user's application to the selected job after user approval.
    Records the application in the system for tracking and history.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with application record and next agent

    Raises:
        ApplicationError: If application submission fails
    """
    logger.info("Starting application agent")

    try:
        # Check if approved
        approved = StateValidator.get(state, "approved", False)
        selected_job = StateValidator.get(state, "selected_job")
        applications = StateValidator.get_list(state, "applications", [])

        if not approved:
            logger.warning("Application not approved; skipping submission")
            application_record = {
                "job": selected_job,
                "status": "skipped",
                "application_submitted": False,
                "reason": "User did not approve",
                "timestamp": datetime.now().isoformat()
            }
            applications.append(record_application(application_record))
        elif not selected_job:
            logger.warning("No job selected; cannot apply")
            application_record = {
                "job": None,
                "status": "failed",
                "application_submitted": False,
                "reason": "No job selected",
                "timestamp": datetime.now().isoformat()
            }
            applications.append(record_application(application_record))
        else:
            job_title = selected_job.get("title", "Unknown")
            company_name = selected_job.get("company", "Unknown")
            logger.info(f"Submitting application for: {job_title} at {company_name}")

            # Record the application internally for history tracking.
            application_record = apply_job(selected_job)
            application_record["timestamp"] = datetime.now().isoformat()
            application_record["application_submitted"] = False
            application_record["status"] = "tracked"
            applications.append(application_record)
            logger.info("Application recorded successfully")

        state["applications"] = applications

        # Update execution plan
        if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Application agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except ApplicationError as e:
        logger.error(f"Application submission failed: {str(e)}")
        state["error"] = str(e)
        applications = StateValidator.get_list(state, "applications", [])
        applications.append({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["applications"] = applications
        raise

    except Exception as e:
        logger.error(f"Unexpected error in application: {str(e)}", exc_info=True)
        state["error"] = str(e)
        applications = StateValidator.get_list(state, "applications", [])
        applications.append({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["applications"] = applications
        raise ApplicationError(f"Application agent failed: {str(e)}") from e
