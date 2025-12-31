#!/usr/bin/env python3
"""
Configuration settings for HTTP Explorer
"""

CONFIG = {
    "user_agent": "Mozilla/5.0 (compatible; DirectoryExplorer/1.0;",
    "request_timeout": 30,
    "download_timeout": 300,
    "history_file": ".explorer_history.json",
    "color_output": True,
    "max_filename_display": 50,
    "chunk_size": 8192 * 8,
}


class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


def colorize(text: str, color_code: str) -> str:
    """Apply color if enabled"""
    return f"{color_code}{text}{Colors.RESET}" if CONFIG["color_output"] else text
