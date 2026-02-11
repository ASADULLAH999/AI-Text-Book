"""Citation validation and confidence scoring models."""

from pydantic import BaseModel, Field
from typing import Optional


class Citation(BaseModel):
    """Citation extracted from generated answer."""

    chunk_id: str = Field(..., description="Referenced chunk ID")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score from reranking"
    )
    is_valid: bool = Field(
        default=True, description="Whether citation passed grounding check"
    )
    validation_error: Optional[str] = Field(
        None, description="Error message if citation failed validation"
    )

    @property
    def confidence_level(self) -> str:
        """Map confidence score to human-readable level.

        Returns:
            str: "high", "medium", or "low" based on confidence_score
        """
        if self.confidence_score >= 0.8:
            return "high"
        elif self.confidence_score >= 0.6:
            return "medium"
        else:
            return "low"

    model_config = {
        "json_schema_extra": {
            "example": {
                "chunk_id": "chunk_4589",
                "confidence_score": 0.92,
                "is_valid": True,
                "validation_error": None,
            }
        }
    }
