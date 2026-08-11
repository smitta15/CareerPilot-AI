from app.graph.state import CareerPilotState

def router(state: CareerPilotState):

    plan = state["execution_plan"]
    step = state["current_step"]

    if step >= len(plan):
        return "END"

    return plan[step]