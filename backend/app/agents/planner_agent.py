"""
Planner Agent - Creates execution plan for the workflow.

Analyzes user request and builds a minimal, efficient execution plan
by selecting appropriate agents and their sequence.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import CareerPilotException

logger = LoggerFactory.get_logger("careerpilot.agents.planner")


def planner_agent(state: CareerPilotState) -> Command:
    """
    Create execution plan for workflow.

    Analyzes the user query and constructs a minimal execution plan
    by selecting appropriate agents and their sequence.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with updated execution plan and next agent

    Raises:
        CareerPilotException: If planning fails after retries
    """
    logger.info("Starting planner agent")

    try:
        # Validate required input
        user_query = StateValidator.get(state, "user_query", required=True)
        logger.debug(f"Planning for query: {user_query}")

        # The API always needs a complete search-to-approval workflow.  Keep
        # routing deterministic so an LLM cannot return invalid graph nodes.
        execution_plan = [
            {"agent": agent, "input": {}, "status": "pending"}
            for agent in (
                "search_agent", "matching_agent", "company_agent",
                "skill_gap_agent", "resume_agent", "decision_agent",
                "application_agent", "report_agent",
            )
        ]

        logger.info(f"Generated execution plan with {len(execution_plan)} tasks")
        logger.debug(f"Tasks: {[t['agent'] for t in execution_plan]}")

        # Update state
        state["execution_plan"] = execution_plan
        state["current_step"] = 0

        logger.info("Planner agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except CareerPilotException as e:
        logger.error(f"Planning failed (CareerPilot error): {str(e)}")
        state["error"] = str(e)
        raise

    except Exception as e:
        logger.error(f"Planning failed unexpectedly: {str(e)}", exc_info=True)
        state["error"] = str(e)
        raise CareerPilotException(f"Planner failed: {str(e)}") from e
