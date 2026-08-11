"""
Decision Agent - Requests user approval before applying.

Presents the analysis and recommendations to the user, requesting
their decision to proceed with the application.
"""

from langgraph.types import Command, interrupt
from langgraph.errors import GraphInterrupt
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import DecisionError
from app.services.decision_service import make_decision

logger = LoggerFactory.get_logger("careerpilot.agents.decision")


def decision_agent(state: CareerPilotState) -> Command:
    """Generate a recommendation and request approval for the selected role."""
    logger.info("Starting decision agent")

    try:
        selected_job = StateValidator.get(state, "selected_job")
        match_score = StateValidator.get(state, "match_score", 0)

        decision = make_decision(state)
        state["decision"] = decision

        if not selected_job:
            logger.warning("No job selected; cannot request decision")
            state["approval_required"] = False
            state["approval_reason"] = "No job was selected"
            state["approved"] = False
            state["decision"] = {
                **decision,
                "decision": "reject",
                "reason": "No job was selected for evaluation.",
                "recommendation": "Select a job before continuing.",
            }
        else:
            job_title = selected_job.get("title", "Unknown Job")
            state["approval_required"] = True
            state["approval_reason"] = (
                f"Ready to track {job_title} at {selected_job.get('company', 'Unknown')}. "
                f"Match score: {match_score}%"
            )
            logger.info("Pausing workflow for user approval")
            approved = interrupt({
                "approval_required": True,
                "approval_reason": state["approval_reason"],
                "selected_job": selected_job,
                "match_score": match_score,
                "decision": decision,
            })
            state["approved"] = bool(approved)
            state["approval_required"] = False

        if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Decision agent completed successfully")
        return Command(update=state, goto=get_next_agent(state))

    except GraphInterrupt:
        raise

    except DecisionError as e:
        logger.error(f"Decision processing failed: {str(e)}")
        state["error"] = str(e)
        raise

    except Exception as e:
        logger.error(f"Unexpected error in decision agent: {str(e)}", exc_info=True)
        state["error"] = str(e)
        raise DecisionError(f"Decision agent failed: {str(e)}") from e
