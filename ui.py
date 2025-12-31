#!/usr/bin/env python3
"""
User Interface components for HTTP Explorer
"""
import os
import time
from typing import Dict, List
import config


class UI:
    """Handles all user interface components"""

    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def display_header():
        """Display application header"""
        print(f"{config.colorize('═' * 80, config.Colors.CYAN)}")
        print(
            f"{config.colorize('🌐 HTTP DIRECTORY EXPLORER (AutoIndex)', config.Colors.BOLD + config.Colors.CYAN)}"
        )
        print(f"{config.colorize('═' * 80, config.Colors.CYAN)}")

    @staticmethod
    def display_directory(items: List[Dict], current_path: str, max_display: int = 600):
        """Display directory contents"""
        dir_count = sum(1 for i in items if i["is_directory"])
        file_count = sum(1 for i in items if i["is_file"])

        print(f"Current: {config.colorize(current_path, config.Colors.YELLOW)}")
        print(f"Items: {len(items)} ({dir_count} dirs, {file_count} files)")
        print(f"{config.colorize('─' * 80, config.Colors.DIM)}")

        dir_idx = 0
        file_idx = 0

        for item in items[:max_display]:
            if item["is_directory"]:
                dir_idx += 1
                display_idx = str(dir_idx)
                prefix = "📁"
                color = config.Colors.BLUE
                type_label = "DIR"
            else:
                file_idx += 1
                display_idx = str(file_idx)
                prefix = "📄"
                color = config.Colors.GREEN
                type_label = "FILE"

            display_name = item["name"]
            if len(display_name) > config.CONFIG["max_filename_display"]:
                display_name = (
                    display_name[: config.CONFIG["max_filename_display"] - 3] + "..."
                )

            size_display = (
                item["size"].rjust(12) if item["size"] != "-" else "--".rjust(12)
            )

            print(
                f"{config.colorize(f'{display_idx:>3}.', color)} {prefix} "
                f"{config.colorize(display_name.ljust(config.CONFIG['max_filename_display']), color)} "
                f"{config.colorize(type_label, config.Colors.DIM):<6} "
                f"{config.colorize(size_display, config.Colors.MAGENTA)} "
                f"{config.colorize(item['last_modified'][:16], config.Colors.DIM)}"
            )

        if len(items) > max_display:
            print(
                f"{config.colorize(f'... and {len(items) - max_display} more items', config.Colors.DIM)}"
            )

        print(f"{config.colorize('─' * 80, config.Colors.DIM)}")

    @staticmethod
    def display_commands():
        """Display available commands"""
        print(f"{config.colorize('📋 COMMANDS:', config.Colors.BOLD)}")
        commands = [
            ("[1-9]", "Select directory/file by number"),
            ("1,3,5", "Download multiple files"),
            ("0", "Download ALL files in current directory"),
            ("a", "Download ALL (recursively from here)"),
            ("b", "Go BACK to previous directory"),
            ("r", "REFRESH current directory"),
            ("s", "Show STATS"),
            ("h", "Show HELP"),
            ("q", "QUIT and save history"),
        ]

        for cmd, desc in commands:
            print(f"  {config.colorize(cmd, config.Colors.YELLOW):<10} - {desc}")

        print(f"{config.colorize('═' * 80, config.Colors.CYAN)}")

    @staticmethod
    def display_stats(session_data: dict, download_path: str):
        """Display session statistics"""
        from utils import format_size

        print(
            f"\n{config.colorize('📊 SESSION STATISTICS', config.Colors.BOLD + config.Colors.CYAN)}"
        )
        print(f"{config.colorize('─' * 50, config.Colors.DIM)}")
        stats = [
            ("Files downloaded", session_data["files_downloaded"], config.Colors.GREEN),
            ("Files skipped", session_data["files_skipped"], config.Colors.YELLOW),
            ("Files failed", session_data["files_failed"], config.Colors.RED),
            (
                "Total data",
                format_size(session_data["total_downloaded"]),
                config.Colors.GREEN,
            ),
        ]

        for label, value, color in stats:
            print(f"{label:<20}: {config.colorize(str(value), color)}")

        print(f"Download folder:  {download_path}")
        print(f"{config.colorize('─' * 50, config.Colors.DIM)}")

    @staticmethod
    def display_help():
        """Display help information"""
        print(
            f"\n{config.colorize('❓ HELP - HOW TO USE', config.Colors.BOLD + config.Colors.CYAN)}"
        )
        print(f"{config.colorize('─' * 60, config.Colors.DIM)}")

        sections = [
            (
                "Navigation:",
                [
                    "• Enter a number to select a directory or file",
                    "• Enter 'b' to go back to the previous directory",
                    "• Enter 'r' to refresh the current directory",
                ],
            ),
            (
                "Downloading:",
                [
                    "• Enter '0' to download ALL files in current directory",
                    "• Enter 'a' to download ALL files recursively",
                    "• Enter '1,3,5' to download specific files",
                    "• Select a file number to download that single file",
                ],
            ),
            (
                "Tips:",
                [
                    "• Files are saved in 'downloads/' folder",
                    "• Directory structure is preserved locally",
                    "• Existing files are skipped if sizes match",
                    "• Partial downloads can be resumed",
                ],
            ),
        ]

        for section, items in sections:
            print(f"{config.colorize(section, config.Colors.BOLD)}")
            for item in items:
                print(f"  {item}")
            print()

        print(f"{config.colorize('─' * 60, config.Colors.DIM)}")

    @staticmethod
    def get_choice() -> str:
        """Get user choice input"""
        return (
            input(f"\n{config.colorize('❯ Enter choice:', config.Colors.BOLD)} ")
            .strip()
            .lower()
        )

    @staticmethod
    def show_message(message: str, msg_type: str = "info"):
        """Show a message to the user"""
        colors = {
            "info": config.Colors.CYAN,
            "success": config.Colors.GREEN,
            "warning": config.Colors.YELLOW,
            "error": config.Colors.RED,
        }

        color = colors.get(msg_type, config.Colors.CYAN)
        print(f"{config.colorize(message, color)}")
        if msg_type in ["info", "success"]:
            time.sleep(1)
