import os
from datetime import datetime
from pathlib import Path


TEMP_DIR = Path("temp")


def ensure_temp_dir():
    """Ensure temp directory exists."""
    TEMP_DIR.mkdir(exist_ok=True)


def save_link_to_txt(filename: str, link: str) -> str:
    """
    Save a link to a txt file in the temp directory.
    
    Args:
        filename: Name of the file (without extension)
        link: URL link to save
        
    Returns:
        Path to the created txt file
    """
    ensure_temp_dir()
    
    # Create safe filename
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    txt_filename = f"{safe_filename}.txt"
    txt_path = TEMP_DIR / txt_filename
    
    # Write link with timestamp
    timestamp = datetime.now().isoformat()
    content = f"# {timestamp}\n{link}\n"
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return str(txt_path)


def read_link_from_txt(filename: str) -> str | None:
    """
    Read a link from a txt file.
    
    Args:
        filename: Name of the file (without extension)
        
    Returns:
        Link content or None if file doesn't exist
    """
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    txt_filename = f"{safe_filename}.txt"
    txt_path = TEMP_DIR / txt_filename
    
    if not txt_path.exists():
        return None
    
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # Return the last non-comment line
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    
    return None