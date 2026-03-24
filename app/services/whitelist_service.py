"""
Service layer for managing whitelist terms.
Replaces the old add_to_whitelist.py script with database-backed logic.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.dictionary import WhitelistTerm

def add_word(db: Session, word: str) -> dict:
    """
    Safely adds a new word to the whitelist database.
    
    Args:
        db: SQLAlchemy database session.
        word: The term to whitelist.
        
    Returns:
        dict: Status and message of the operation.
    """
    word = word.strip()
    
    if not word:
        return {"status": "ERROR", "message": "No word provided"}

    try:
        # Check if the word already exists
        existing_term = db.query(WhitelistTerm).filter(WhitelistTerm.word == word).first()
        
        if existing_term:
            return {"status": "SKIPPED", "message": f"'{word}' is already in the whitelist."}

        # Create new term
        new_term = WhitelistTerm(word=word, hit_count=0)
        db.add(new_term)
        db.commit()
        
        return {"status": "SUCCESS", "message": f"Successfully added '{word}' to whitelist."}
        
    except IntegrityError:
        # Handle concurrent inserts gracefully
        db.rollback()
        return {"status": "SKIPPED", "message": f"'{word}' is already in the whitelist."}
    except Exception as e:
        db.rollback()
        return {"status": "ERROR", "message": str(e)}
