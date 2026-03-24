"""
Service layer for pre-filtering prompts.
Replaces the old pre_filter.py script with database-backed logic.
"""
from sqlalchemy.orm import Session
from app.models.dictionary import WhitelistTerm

def check_prompt(db: Session, prompt: str) -> dict:
    """
    Checks if a prompt can bypass LLM semantic analysis.
    
    Args:
        db: SQLAlchemy database session.
        prompt: The user's input prompt.
        
    Returns:
        dict: Status and message indicating whether to PASS or NEEDS_LLM.
    """
    prompt = prompt.strip()
    
    if not prompt:
        return {"status": "NEEDS_LLM", "reason": "No prompt provided"}

    # Rule 1: Fast Pass for short generic confirmations (e.g., "ok", "yes", "1")
    if len(prompt) <= 2 and prompt.isascii():
        return {"status": "PASS", "message": "Short generic confirmation."}

    # Rule 2: Fast Pass for exact whitelist match
    try:
        term = db.query(WhitelistTerm).filter(WhitelistTerm.word == prompt).first()
        if term:
            # Increment hit count for telemetry
            term.hit_count += 1
            db.commit()
            return {"status": "PASS", "message": "Exact whitelist match."}
    except Exception as e:
        db.rollback()
        # Log error in production, but fallback to LLM gracefully
        pass

    # Default: Fallback to LLM for deep semantic check
    return {"status": "NEEDS_LLM", "message": "Requires deep semantic analysis."}
