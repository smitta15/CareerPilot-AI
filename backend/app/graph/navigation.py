from langgraph.graph import END


def get_next_agent(state):

    plan = state["execution_plan"]
    step = state["current_step"]

    if step >= len(plan):
        return END

    return plan[step]["agent"]