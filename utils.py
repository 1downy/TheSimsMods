#!/usr/bin/env python3
"""
Utility functions for HTTP Explorer
"""
import re
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import config


def clean_name(name: str) -> str:
    """Clean up file/directory names from HTML artifacts"""
    if not name:
        return ""

    name = re.sub(r"\b(parent directory|up|\.\.)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"<[^>]+>", "", name)
    name = re.sub(
        r"[\s▸▹▶›>•\-⇧↑↥⇑⬆↗→↘↓↙←↖↕↔↩↪↵⌫⎆☐☑☒⚐⚑♠♣♥♦♤♧♡♢†‡•°·…※×÷±¬^~|\\]", " ", name
    )

    name = re.sub(r"\s+", " ", name)

    return name.strip()


def clean_text(text: str) -> str:
    """Clean up text fields"""
    if not text:
        return ""
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_file_size(size_str: str) -> int:
    """Parse file size string to bytes - handles formats like '2977k', '8545k', '117k'"""
    if not size_str or size_str == "-":
        return 0

    size_str = size_str.strip().lower()
    if "k" in size_str:
        try:
            size_kb = float(size_str.replace("k", ""))
            return int(size_kb * 1024)
        except:
            return 0
    try:
        clean_str = re.sub(r"[^\d.]", "", size_str)
        if clean_str:
            return int(float(clean_str))
    except:
        pass

    return 0


def format_size(size_bytes: int) -> str:
    """Format file size human-readable"""
    if size_bytes == 0:
        return "0B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f}PB"


def build_local_path(base_path: Path, file_url: str, base_url: str) -> Path:
    """Build local file path from URL"""
    from urllib.parse import urlparse

    url_path = urlparse(file_url).path
    base_url_path = urlparse(base_url).path
    if url_path.startswith(base_url_path):
        rel_path = url_path[len(base_url_path) :].lstrip("/")
    else:
        rel_path = url_path.lstrip("/")

    return base_path / rel_path


def save_session_data(
    session_data: Dict[str, Any], history_file: str, current_url: str, history: list
) -> bool:
    """Save session history to file"""
    try:
        history_data = {
            "session": session_data,
            "last_location": current_url,
            "history": history,
            "saved_at": datetime.now().isoformat(),
        }

        with open(history_file, "w") as f:
            import json

            json.dump(history_data, f, indent=2)
        return True
    except Exception:
        return False


def load_session_data(history_file: str) -> Dict[str, Any]:
    """Load session history from file"""
    try:
        if Path(history_file).exists():
            with open(history_file, "r") as f:
                import json

                return json.load(f)
    except Exception:
        pass
    return {}
