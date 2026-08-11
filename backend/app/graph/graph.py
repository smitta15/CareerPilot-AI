from langgraph.graph import StateGraph, START

from app.graph.state import CareerPilotState

from app.agents.planner_agent import planner_agent
from app.agents.search_agent import search_agent
from app.agents.matching_agent import matching_agent
from app.agents.resume_agent import resume_agent
from app.agents.company_agent import company_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.agents.decision_agent import decision_agent
from app.agents.application_agent import application_agent
from app.agents.report_agent import report_agent


def build_graph(checkpointer=None):

    builder = StateGraph(CareerPilotState)

    builder.add_node("planner", planner_agent)
    builder.add_node("search_agent", search_agent)
    builder.add_node("matching_agent", matching_agent)
    builder.add_node("resume_agent", resume_agent)
    builder.add_node("company_agent", company_agent)
    builder.add_node("skill_gap_agent", skill_gap_agent)
    builder.add_node("decision_agent", decision_agent)
    builder.add_node("application_agent", application_agent)
    builder.add_node("report_agent", report_agent)

    builder.add_edge(START, "planner")

    return builder.compile(
        checkpointer=checkpointer
    )