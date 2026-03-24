"""
Service layer for codebase indexing.
Replaces the old extract_project_terms.py script with database-backed background tasks.
"""
import os
import re
import json
import time
import subprocess
from sqlalchemy.orm import Session
from app.models.dictionary import ProjectTerm

def get_config() -> dict:
    """Load configuration for scanning extensions and ignored directories."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # Fallback default configuration
        return {
            "ignore_dirs": [".git", "node_modules", "venv", ".env", "__pycache__", "dist", "build", ".cursor"],
            "valid_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".md", ".txt", ".json", ".yml", ".yaml"]
        }

def get_project_root() -> str:
    """
    Dynamically resolve project root by looking for common root markers.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    markers = ['.git', 'package.json', 'pyproject.toml', 'pom.xml', 'go.mod', 'requirements.txt']
    
    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
        
    return os.getcwd()

def get_git_tracked_files(root_dir: str) -> list[str] | None:
    """
    Use Git to get tracked files, respecting .gitignore.
    """
    try:
        result = subprocess.run(
            ['git', 'ls-files'], 
            cwd=root_dir, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=True
        )
        files = result.stdout.splitlines()
        return [os.path.join(root_dir, f) for f in files]
    except Exception as e:
        print(f"Git ls-files failed. Fallback to os.walk. Error: {e}")
        return None

def extract_terms_from_text(text: str) -> set[str]:
    """Extract CamelCase and snake_case terms from text."""
    terms = set()
    camel_case = re.findall(r'\b[A-Z][a-zA-Z0-9]+\b', text)
    snake_case = re.findall(r'\b[a-z]+_[a-z0-9_]+\b', text)
    terms.update(camel_case)
    terms.update(snake_case)
    return terms

def scan_project(root_dir: str, config: dict) -> tuple[list[str], int]:
    """Scans the project directory and extracts specific terminology."""
    project_terms = set()
    file_count = 0
    valid_exts = set(config.get("valid_extensions", []))
    ignore_dirs = set(config.get("ignore_dirs", []))
    
    files_to_scan = get_git_tracked_files(root_dir)
    
    if files_to_scan is None:
        files_to_scan = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for filename in filenames:
                files_to_scan.append(os.path.join(dirpath, filename))
                
    for filepath in files_to_scan:
        filename = os.path.basename(filepath)
        
        # 1. Extract base filename
        base_name = os.path.splitext(filename)[0]
        if len(base_name) > 2:
            project_terms.add(base_name)
        
        # 2. Extract terms from file content
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_exts:
            try:
                # Limit file size to 500KB to prevent memory issues
                if os.path.getsize(filepath) < 500 * 1024:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        terms = extract_terms_from_text(content)
                        project_terms.update(terms)
                        file_count += 1
            except Exception:
                pass
                    
    return list(project_terms), file_count

def scan_project_background(db: Session) -> None:
    """
    Background task entry point for FastAPI.
    Scans the project and updates the ProjectTerm table.
    """
    start_time = time.time()
    print("Starting background project indexing...")
    
    try:
        config = get_config()
        root_dir = get_project_root()
        terms, file_count = scan_project(root_dir, config)
        
        # Filter out short words and pure numbers
        terms = [t for t in terms if len(t) > 2 and not t.isdigit()]
        
        # Database Operations: Clear old terms and bulk insert new ones
        db.query(ProjectTerm).delete()
        
        # Prepare bulk objects
        db_terms = [ProjectTerm(word=t) for t in set(terms)]
        
        # Bulk save
        db.bulk_save_objects(db_terms)
        db.commit()
        
        elapsed = time.time() - start_time
        print(f"Indexing complete in {elapsed:.2f} seconds.")
        print(f"Scanned {file_count} files. Extracted {len(terms)} project terms.")
        
    except Exception as e:
        db.rollback()
        print(f"Background scanning failed: {e}")
