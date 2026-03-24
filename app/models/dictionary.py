"""
Database models for the prompt-corrector skill.
Defines the schema for WhitelistTerm and ProjectTerm using SQLAlchemy 2.0.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class WhitelistTerm(Base):
    """
    Represents a term that has been explicitly whitelisted by the user.
    These terms bypass the LLM spelling correction.
    """
    __tablename__ = "whitelist_terms"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    hit_count = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<WhitelistTerm(word='{self.word}', hits={self.hit_count})>"


class ProjectTerm(Base):
    """
    Represents a term automatically extracted from the project's codebase.
    These terms bypass the LLM spelling correction.
    """
    __tablename__ = "project_terms"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<ProjectTerm(word='{self.word}')>"
