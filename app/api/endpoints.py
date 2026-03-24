"""
FastAPI route controllers.
Maps HTTP requests to the underlying service layer logic.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.schemas import FilterRequest, WhitelistRequest, StandardResponse
from app.services import filter_service, whitelist_service, scanner_service

router = APIRouter()

@router.post("/filter", response_model=StandardResponse)
def check_prompt(request: FilterRequest, db: Session = Depends(get_db)):
    """
    Analyzes the user's prompt to determine if it can bypass LLM semantic analysis.
    Checks against the whitelist and generic short confirmations.
    """
    result = filter_service.check_prompt(db=db, prompt=request.prompt)
    return StandardResponse(**result)

@router.post("/whitelist", response_model=StandardResponse)
def add_to_whitelist(request: WhitelistRequest, db: Session = Depends(get_db)):
    """
    Safely adds a new term to the whitelist database.
    Ensures thread safety and prevents duplicates.
    """
    result = whitelist_service.add_word(db=db, word=request.word)
    return StandardResponse(**result)

@router.post("/scan", response_model=StandardResponse, status_code=202)
def trigger_project_scan(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers a background task to index the project's codebase.
    Extracts domain-specific terminology (CamelCase, snake_case) and filenames.
    Returns immediately without blocking the client.
    """
    background_tasks.add_task(scanner_service.scan_project_background, db)
    return StandardResponse(
        status="ACCEPTED",
        message="Project scanning started in the background."
    )
