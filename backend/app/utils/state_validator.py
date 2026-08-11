"""
State utility functions for safe state access and validation.

Provides defensive getters, validators, and state initialization
to prevent common state-related errors in agents.
"""

from typing import Any, Optional, Type, TypeVar, Dict, List
from app.graph.state import CareerPilotState
from app.exceptions import StateValidationError
from app.logging_config import LoggerFactory

logger = LoggerFactory.get_logger("careerpilot.state")

T = TypeVar("T")


class StateValidator:
    """Utility for safe state access and validation."""

    @staticmethod
    def get(
        state: CareerPilotState,
        key: str,
        default: Optional[T] = None,
        required: bool = False,
    ) -> Optional[T]:
        """
        Safely get value from state with validation.

        Args:
            state: Current CareerPilot state
            key: State key to retrieve
            default: Default value if key missing
            required: If True, raise error if missing

        Returns:
            Value from state or default

        Raises:
            StateValidationError: If required key is missing
        """
        value = state.get(key, default)

        if value is None and required:
            raise StateValidationError(
                f"Required state field '{key}' is missing or None"
            )

        if value is None:
            logger.debug(f"State field '{key}' is None, using default: {default}")

        return value

    @staticmethod
    def get_list(
        state: CareerPilotState,
        key: str,
        default: Optional[List] = None,
    ) -> List:
        """
        Safely get list from state.

        Args:
            state: Current state
            key: State key for list
            default: Default empty list if missing

        Returns:
            List from state or default
        """
        value = state.get(key, default or [])

        if not isinstance(value, list):
            logger.warning(f"State field '{key}' is not a list: {type(value)}")
            return default or []

        return value

    @staticmethod
    def get_dict(
        state: CareerPilotState,
        key: str,
        default: Optional[Dict] = None,
    ) -> Dict:
        """
        Safely get dict from state.

        Args:
            state: Current state
            key: State key for dict
            default: Default empty dict if missing

        Returns:
            Dict from state or default
        """
        value = state.get(key, default or {})

        if not isinstance(value, dict):
            logger.warning(f"State field '{key}' is not a dict: {type(value)}")
            return default or {}

        return value

    @staticmethod
    def validate_required_fields(
        state: CareerPilotState,
        fields: List[str],
    ) -> None:
        """
        Validate that all required fields exist in state.

        Args:
            state: Current state
            fields: List of required field names

        Raises:
            StateValidationError: If any required field is missing
        """
        missing = [f for f in fields if f not in state or state[f] is None]

        if missing:
            raise StateValidationError(
                f"Missing required state fields: {', '.join(missing)}"
            )

        logger.debug(f"Validated {len(fields)} required state fields")

    @staticmethod
    def initialize_lists(state: CareerPilotState) -> None:
        """
        Initialize all list fields to empty lists if not set.

        Prevents KeyError and type errors in agents.

        Args:
            state: Current state (modified in place)
        """
        list_fields = [
            "execution_plan",
            "opportunities",
            "shortlisted_jobs",
            "analyzed_jobs",
            "applications",
        ]

        for field in list_fields:
            if field not in state or not isinstance(state.get(field), list):
                state[field] = []
                logger.debug(f"Initialized '{field}' to empty list")

    @staticmethod
    def initialize_dicts(state: CareerPilotState) -> None:
        """
        Initialize all dict fields to empty dicts if not set.

        Args:
            state: Current state (modified in place)
        """
        dict_fields = ["profile", "final_response", "company_report", "skill_gap"]

        for field in dict_fields:
            if field not in state or not isinstance(state.get(field), dict):
                state[field] = {}
                logger.debug(f"Initialized '{field}' to empty dict")

    @staticmethod
    def create_initial_state(user_query: str, profile: Optional[Dict] = None) -> CareerPilotState:
        """
        Create a properly initialized initial state.

        Args:
            user_query: User's search query
            profile: User's profile data (optional)

        Returns:
            Initialized CareerPilotState
        """
        state: CareerPilotState = {
            "user_query": user_query,
            "search_query": "",
            "execution_plan": [],
            "current_step": 0,
            "profile": profile or {},
            "opportunities": [],
            "shortlisted_jobs": [],
            "analyzed_jobs": [],
            "applications": [],
            "approval_required": False,
            "approval_reason": "",
            "approved": False,
            "decision": {},
            "match_score": 0,
            "match_reason": "",
            "final_response": {},
            "selected_job": None,
            "company_report": None,
            "skill_gap": None,
            "tailored_resume": None,
            "thread_id": None,
            "error": None,
        }

        logger.info(f"Created initial state with user_query={user_query}")
        return state

    @staticmethod
    def copy_state(state: CareerPilotState) -> CareerPilotState:
        """
        Create a deep copy of state to prevent mutations.

        Args:
            state: Current state

        Returns:
            New copy of state
        """
        import copy

        return copy.deepcopy(state)
