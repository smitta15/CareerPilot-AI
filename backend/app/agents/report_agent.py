"""
Report Agent - Generates final workflow summary.

Creates a comprehensive report of the entire workflow including
analysis results, recommendations, and next steps.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.services.report_service import generate_report
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import ReportGenerationError

logger = LoggerFactory.get_logger("careerpilot.agents.report")


def report_agent(state: CareerPilotState) -> Command:
    """
    Generate final workflow report.

    Creates a comprehensive summary of the workflow including job details,
    analysis results, recommendations, and next steps.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with final report and next agent

    Raises:
        ReportGenerationError: If report generation fails
    """
    logger.info("Starting report agent")

    try:
        # Generate report with defensive access
        logger.debug("Generating report from state")

        with logger.timer("Report generation"):
            report = generate_report(state)

        logger.info("Report generated successfully")
        state["final_response"] = report or {}

        # Update execution plan
        try:
            if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
                task = state["execution_plan"][state["current_step"]]
                task["status"] = "completed"
                state["current_step"] = state.get("current_step", 0) + 1
        except (IndexError, KeyError) as e:
            logger.warning(f"Could not update execution plan: {str(e)}")

        logger.info("Report agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except ReportGenerationError as e:
        logger.error(f"Report generation failed: {str(e)}")
        state["error"] = str(e)
        state["final_response"] = {"error": str(e)}
        raise

    except Exception as e:
        logger.error(f"Unexpected error in report generation: {str(e)}", exc_info=True)
        state["error"] = str(e)
        state["final_response"] = {"error": str(e)}
        raise ReportGenerationError(f"Report agent failed: {str(e)}") from e
