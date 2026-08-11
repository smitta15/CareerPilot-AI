"""
FastAPI application for CareerPilot AI.

Exposes REST API endpoints for:
- Job search and analysis
- Job application tracking
- Resume management
"""

from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from app.settings import settings
from app.logging_config import setup_logging, LoggerFactory
from app.graph.graph import build_graph
from app.runtime.checkpoint import checkpoint
from app.models.request_models import JobRequest, ResumeRequest, AnalyzeRequest, ApplyRequest
from app.models.analyzed_job import AnalyzedJob
from app.services.application_service import get_applications
from app.exceptions import CareerPilotException
from app.utils.state_validator import StateValidator

setup_logging()
logger = LoggerFactory.get_logger("careerpilot.api")


def _graph_or_503():
    """Return the initialized graph or a client-safe readiness error."""
    graph = getattr(app.state, "graph", None)
    if graph is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return graph


def _thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _state_for_thread(graph, thread_id: str) -> dict:
    """Load checkpointed state and turn missing/unknown threads into a 404."""
    snapshot = graph.get_state(_thread_config(thread_id))
    state = getattr(snapshot, "values", None)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow thread not found")
    return state


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("CareerPilot AI starting...")

    missing_vars = settings.validate()
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    logger.info(f"Configuration loaded: {settings.to_dict()}")

    try:
        with checkpoint() as saver:
            app.state.graph = build_graph(checkpointer=saver)
            logger.info("LangGraph workflow initialized successfully")
            yield
    except Exception as e:
        logger.critical(f"Failed to initialize graph: {str(e)}", exc_info=True)
        raise

    logger.info("CareerPilot AI shutting down...")


app = FastAPI(
    title="CareerPilot AI",
    description="AI-powered internship assistant with LangGraph workflow",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CareerPilotException)
async def careerpilot_exception_handler(request: Request, exc: CareerPilotException):
    logger.error(f"CareerPilot error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_type": "InternalServerError"},
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareerPilot AI",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready")
def readiness_check():
    try:
        if not hasattr(app.state, "graph"):
            raise RuntimeError("Graph not initialized")
        return {"status": "ready", "graph_initialized": True}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/chat")
def chat(request: JobRequest):
    request_id = str(uuid.uuid4())
    LoggerFactory.set_request_id(request_id)
    logger.info(f"Starting chat for query: {request.user_query}")

    try:
        graph = _graph_or_503()
        thread_id = str(uuid.uuid4())
        profile = {"skills": ["Python", "Java", "SQL", "Git", "FastAPI"]}
        state = StateValidator.create_initial_state(user_query=request.user_query, profile=profile)
        state["thread_id"] = thread_id

        with logger.timer("Graph execution for /chat"):
            result = graph.invoke(state, config=_thread_config(thread_id))

        logger.info(f"Chat completed successfully with thread_id={thread_id}")
        return {"thread_id": thread_id, "request_id": request_id, "result": result}

    except GraphInterrupt:
        graph = _graph_or_503()
        state = graph.get_state(_thread_config(thread_id)).values if "thread_id" in locals() else {}
        return {
            "thread_id": thread_id if "thread_id" in locals() else None,
            "request_id": request_id,
            "status": "awaiting_approval",
            "approval_required": True,
            "result": state,
        }
    except CareerPilotException as e:
        logger.warning(f"CareerPilot error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph invocation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        LoggerFactory.clear_request_id()


@app.post("/resume")
def resume(request: ResumeRequest):
    request_id = str(uuid.uuid4())
    LoggerFactory.set_request_id(request_id)
    logger.info(f"Resuming workflow for thread_id={request.thread_id}")

    try:
        graph = _graph_or_503()
        with logger.timer("Graph resume execution"):
            result = graph.invoke(Command(resume=request.approved), config=_thread_config(request.thread_id))
        logger.info(f"Resume completed with approval={request.approved}")
        return {"thread_id": request.thread_id, "request_id": request_id, "result": result}

    except GraphInterrupt:
        graph = _graph_or_503()
        state = graph.get_state(_thread_config(request.thread_id)).values
        return {
            "thread_id": request.thread_id,
            "request_id": request_id,
            "status": "awaiting_approval",
            "approval_required": True,
            "result": state,
        }
    except CareerPilotException as e:
        logger.warning(f"CareerPilot error during resume: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph resume failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        LoggerFactory.clear_request_id()


@app.post("/analyze-job", response_model=AnalyzedJob)
def analyze_job(request: AnalyzeRequest):
    request_id = str(uuid.uuid4())
    LoggerFactory.set_request_id(request_id)
    logger.info(f"Analyzing job for thread_id={request.thread_id}, job_index={request.job_index}")

    if not request.thread_id:
        raise HTTPException(status_code=400, detail="thread_id is required")

    try:
        graph = _graph_or_503()
        state = _state_for_thread(graph, request.thread_id)

        if request.job_index is not None:
            jobs = StateValidator.get_list(state, "shortlisted_jobs", [])
            if request.job_index >= len(jobs):
                raise HTTPException(status_code=404, detail="Job index not found")
            selected_job = jobs[request.job_index]
            if not isinstance(selected_job, dict):
                raise HTTPException(status_code=500, detail="Invalid job data in workflow state")
            state["selected_job"] = selected_job
            state["match_score"] = selected_job.get("match_score", 0)
            state["match_reason"] = selected_job.get("match_reason", "")
            graph.update_state(_thread_config(request.thread_id), {
                "selected_job": state["selected_job"],
                "match_score": state["match_score"],
                "match_reason": state["match_reason"],
            })

        selected_job = StateValidator.get_dict(state, "selected_job", {})
        match_score = StateValidator.get(state, "match_score", 0)
        match_reason = StateValidator.get(state, "match_reason", "")
        company_report = StateValidator.get_dict(state, "company_report", {})
        skill_gap = StateValidator.get_dict(state, "skill_gap", {})
        tailored_resume = StateValidator.get(state, "tailored_resume", "") or ""
        decision = StateValidator.get_dict(state, "decision", {})

        analyzed = AnalyzedJob(
            job=selected_job,
            match_score=int(match_score or 0),
            match_reason=match_reason,
            company_report=company_report,
            skill_gap=skill_gap,
            tailored_resume=tailored_resume,
            decision=decision or None,
            status="analyzed",
        )

        logger.info(f"Job analysis completed with score={analyzed.match_score}")
        return analyzed

    except CareerPilotException as e:
        logger.warning(f"CareerPilot error during analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze job")
    finally:
        LoggerFactory.clear_request_id()


@app.post("/apply")
def apply(request: ApplyRequest):
    request_id = str(uuid.uuid4())
    LoggerFactory.set_request_id(request_id)
    logger.info(f"Applying to job for thread_id={request.thread_id}, approved={request.approved}")

    if not request.thread_id:
        raise HTTPException(status_code=400, detail="thread_id is required")

    try:
        graph = _graph_or_503()
        with logger.timer("Graph execution for /apply"):
            raw = graph.invoke(Command(resume=request.approved), config=_thread_config(request.thread_id))

        state = raw if isinstance(raw, dict) else _state_for_thread(graph, request.thread_id)
        apps = StateValidator.get_list(state, "applications", get_applications())
        logger.info(f"Application workflow completed; total applications: {len(apps)}")

        recorded = bool(request.approved and state.get("selected_job"))
        return {
            "request_id": request_id,
            "applications": apps,
            "status": "tracked" if request.approved else "skipped",
            "application_recorded": recorded,
            "application_submitted": False,
            "message": "Application recorded internally for tracking. No external employer submission was performed.",
        }

    except CareerPilotException as e:
        logger.warning(f"CareerPilot error during apply: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Application submission failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to track application")
    finally:
        LoggerFactory.clear_request_id()


@app.get("/applications")
def list_applications():
    logger.info("Listing applications")

    try:
        apps = get_applications()
        logger.debug(f"Retrieved {len(apps)} applications")
        return {"applications": apps, "count": len(apps)}
    except Exception as e:
        logger.error(f"Failed to list applications: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")
