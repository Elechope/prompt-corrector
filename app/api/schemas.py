"""
Pydantic schemas for request and response validation.
Provides automatic OpenAPI documentation and strict type checking.
"""
from pydantic import BaseModel, Field

class FilterRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to be analyzed for typos or jargon.")

class WhitelistRequest(BaseModel):
    word: str = Field(..., description="The specific term to add to the whitelist.")

class StandardResponse(BaseModel):
    status: str = Field(..., description="Status code (e.g., PASS, NEEDS_LLM, SUCCESS, ERROR)")
    message: str = Field(..., description="Human-readable message explaining the result.")
    reason: str | None = Field(None, description="Optional reason for the status.")
