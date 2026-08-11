from langgraph.types import Command

from app.graph.navigation import get_next_agent
from app.graph.state import CareerPilotState


def complete_task(state: CareerPilotState):

    state["execution_plan"][state["current_step"]]["status"] = "completed"

    state["current_step"] += 1

    return Command(
        update=state,
        goto=get_next_agent(state)
    )