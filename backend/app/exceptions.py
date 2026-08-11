"""
Custom exceptions for CareerPilot AI.

Provides domain-specific exceptions for better error handling and logging.
"""


class CareerPilotException(Exception):
    """Base exception for all CareerPilot errors."""

    pass


class ConfigurationError(CareerPilotException):
    """Raised when configuration is invalid or incomplete."""

    pass


class APIError(CareerPilotException):
    """Raised when external API calls fail."""

    pass


class SearchError(APIError):
    """Raised when job search fails."""

    pass


class JobParsingError(CareerPilotException):
    """Raised when job data cannot be parsed."""

    pass


class MatchingError(CareerPilotException):
    """Raised when job matching fails."""

    pass


class CompanyResearchError(CareerPilotException):
    """Raised when company research fails."""

    pass


class SkillGapAnalysisError(CareerPilotException):
    """Raised when skill gap analysis fails."""

    pass


class ResumeTailoringError(CareerPilotException):
    """Raised when resume tailoring fails."""

    pass


class DecisionError(CareerPilotException):
    """Raised when decision generation fails."""

    pass


class ApplicationError(CareerPilotException):
    """Raised when application submission fails."""

    pass


class ReportGenerationError(CareerPilotException):
    """Raised when final report generation fails."""

    pass


class StateValidationError(CareerPilotException):
    """Raised when state validation fails."""

    pass


class DatabaseError(CareerPilotException):
    """Raised when database operations fail."""

    pass
