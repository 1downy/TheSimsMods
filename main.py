#!/usr/bin/env python3
"""
Main entry point for HTTP Explorer
"""
import sys
import signal
import urllib.parse
from pathlib import Path
from datetime import datetime

import config
from parser import AutoIndexParser
from downloader import FileDownloader
from ui import UI
import utils


class HTTPExplorer:
    """Main application controller"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.current_url = self.base_url
        self.history = []

        self.parser = AutoIndexParser()
        self.ui = UI()
        self.downloader = None

        self.session_data = self._init_session_data()
        self.downloader = FileDownloader(self.session_data)

        self.download_base = Path("downloads")
        self.download_base.mkdir(exist_ok=True)

        signal.signal(signal.SIGINT, self._signal_handler)

    def _init_session_data(self) -> dict:
        """Initialize session data"""
        return {
            "start_time": datetime.now().isoformat(),
            "total_downloaded": 0,
            "files_downloaded": 0,
            "files_skipped": 0,
            "files_failed": 0,
        }

    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.ui.show_message("\n⚠️  Interrupted by user", "warning")
        self._save_history()
        sys.exit(0)

    def _save_history(self):
        """Save session history"""
        if utils.save_session_data(
            self.session_data,
            config.CONFIG["history_file"],
            self.current_url,
            self.history,
        ):
            self.ui.show_message("💾 History saved", "success")

    def _load_history(self):
        """Load previous session"""
        history_data = utils.load_session_data(config.CONFIG["history_file"])
        if history_data:
            self.ui.show_message(
                f"📖 Loaded previous session from {history_data['saved_at'][:10]}",
                "info",
            )
            if input("Restore last location? (y/N): ").lower() == "y":
                self.current_url = history_data["last_location"]
                self.history = history_data["history"]
                return True
        return False

    def _fetch_url(self, url: str) -> str:
        """Fetch URL content"""
        import urllib.request

        req = urllib.request.Request(
            url, headers={"User-Agent": config.CONFIG["user_agent"]}
        )

        try:
            with urllib.request.urlopen(
                req, timeout=config.CONFIG["request_timeout"]
            ) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")

    def _process_directory(self):
        """Process current directory"""
        try:
            html = self._fetch_url(self.current_url)
            items = self.parser.parse(html)

            directories = [i for i in items if i["is_directory"]]
            files = [i for i in items if i["is_file"]]

            # ui
            self.ui.clear_screen()
            self.ui.display_header()
            self.ui.display_directory(items, self.current_url)
            self.ui.display_commands()

            choice = self.ui.get_choice()
            self._handle_choice(choice, directories, files, items)

        except Exception as e:
            self.ui.show_message(f"✗ Error: {str(e)}", "error")
            if self.history:
                self.current_url = self.history.pop()
            time.sleep(2)

    def _handle_choice(self, choice: str, directories: list, files: list, items: list):
        """Handle user choice"""
        handlers = {
            "q": self._handle_quit,
            "b": self._handle_back,
            "r": lambda: None,
            "s": self._handle_stats,
            "h": self._handle_help,
            "0": lambda: self._handle_download_all(files),
            "a": lambda: self._handle_recursive_download(),
            ",": lambda: self._handle_multiple_files(choice, files),
        }

        if choice in handlers:
            if choice == "r":
                return
            handlers[choice]()

        # check no
        elif choice.isdigit():
            self._handle_single_number(int(choice), directories, files, items)

        elif "," in choice:
            self._handle_multiple_files(choice, files)

        else:
            self.ui.show_message("✗ Invalid input", "error")
            time.sleep(1)

    def _handle_quit(self):
        """Handle quit command"""
        self.ui.show_message("👋 Goodbye!", "success")
        self._save_history()
        self._show_final_stats()
        sys.exit(0)

    def _handle_back(self):
        """Handle back command"""
        if self.history:
            self.current_url = self.history.pop()
        else:
            self.ui.show_message("ℹ️ No history to go back", "info")
            time.sleep(1)

    def _handle_stats(self):
        """Handle stats command"""
        self.ui.display_stats(self.session_data, str(self.download_base.absolute()))
        input(f"\n{config.colorize('Press Enter to continue...', config.Colors.DIM)}")

    def _handle_help(self):
        """Handle help command"""
        self.ui.display_help()
        input(f"\n{config.colorize('Press Enter to continue...', config.Colors.DIM)}")

    def _handle_download_all(self, files: list):
        """Handle download all files in current directory"""
        if not files:
            self.ui.show_message("ℹ️ No files to download", "info")
            return

        self.ui.show_message(f"📥 Downloading {len(files)} files...", "info")

        for file_item in files:
            file_url = urllib.parse.urljoin(self.current_url + "/", file_item["href"])
            local_path = utils.build_local_path(
                self.download_base, file_url, self.base_url
            )
            self.downloader.download(file_url, local_path)

        self.ui.show_message("✅ Downloads completed", "success")
        input(f"\n{config.colorize('Press Enter to continue...', config.Colors.DIM)}")

    def _handle_recursive_download(self):
        """Handle recursive download"""
        print(
            f"\n{config.colorize('⚠️  RECURSIVE DOWNLOAD WARNING', config.Colors.YELLOW + config.Colors.BOLD)}"
        )
        print(
            f"This will download ALL files from {self.current_url} and all subdirectories."
        )
        confirm = input("Are you sure? This could take a long time! (yes/NO): ").lower()

        if confirm == "yes":
            self._perform_recursive_download(
                self.current_url,
                self.download_base
                / urllib.parse.urlparse(self.current_url).path.lstrip("/"),
            )
            self.ui.show_message("✅ Recursive download completed!", "success")
            self.ui.display_stats(self.session_data, str(self.download_base.absolute()))
            input(
                f"\n{config.colorize('Press Enter to continue...', config.Colors.DIM)}"
            )
        else:
            self.ui.show_message("✗ Cancelled", "warning")
            time.sleep(1)

    def _perform_recursive_download(self, url: str, base_path: Path):
        """Perform recursive download"""
        try:
            html = self._fetch_url(url)
            items = self.parser.parse(html)

            for item in items:
                if item["is_directory"]:
                    sub_url = urllib.parse.urljoin(url + "/", item["href"])
                    sub_path = base_path / item["name"]
                    self.ui.show_message(f"📁 Entering: {item['name']}", "info")
                    self._perform_recursive_download(sub_url, sub_path)
                elif item["is_file"]:
                    file_url = urllib.parse.urljoin(url + "/", item["href"])
                    local_path = base_path / item["name"]
                    self.downloader.download(file_url, local_path)

        except Exception as e:
            self.ui.show_message(f"✗ Error in {url}: {str(e)}", "error")

    def _handle_multiple_files(self, choice: str, files: list):
        """Handle multiple file selection"""
        indices = []
        for part in choice.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= len(files):
                    indices.append(idx - 1)

        if not indices:
            self.ui.show_message("✗ Invalid file numbers", "error")
            return

        self.ui.show_message(f"📥 Downloading {len(indices)} selected files...", "info")

        for file_idx in indices:
            file_item = files[file_idx]
            file_url = urllib.parse.urljoin(self.current_url + "/", file_item["href"])
            local_path = utils.build_local_path(
                self.download_base, file_url, self.base_url
            )
            self.downloader.download(file_url, local_path)

        self.ui.show_message("✅ Selected downloads completed", "success")
        input(f"\n{config.colorize('Press Enter to continue...', config.Colors.DIM)}")

    def _handle_single_number(
        self, idx: int, directories: list, files: list, items: list
    ):
        """Handle single number selection"""
        if 1 <= idx <= len(directories):
            dir_item = directories[idx - 1]
            new_url = urllib.parse.urljoin(self.current_url + "/", dir_item["href"])
            self.history.append(self.current_url)
            self.current_url = new_url

        elif len(directories) < idx <= len(items):
            file_idx = idx - len(directories) - 1
            if 0 <= file_idx < len(files):
                file_item = files[file_idx]
                file_url = urllib.parse.urljoin(
                    self.current_url + "/", file_item["href"]
                )
                local_path = utils.build_local_path(
                    self.download_base, file_url, self.base_url
                )

                self.ui.show_message(f"📥 Downloading: {file_item['name']}", "info")
                self.downloader.download(file_url, local_path)
                input(
                    f"\n{config.colorize('Press Enter to continue...', config.Colors.DIM)}"
                )
            else:
                self.ui.show_message("✗ Invalid file number", "error")
                time.sleep(1)
        else:
            self.ui.show_message("✗ Invalid number", "error")
            time.sleep(1)

    def _show_final_stats(self):
        """Show final session statistics"""
        from utils import format_size

        print(
            f"\n{config.colorize('📊 FINAL SESSION SUMMARY', config.Colors.BOLD + config.Colors.CYAN)}"
        )
        print(f"{config.colorize('═' * 50, config.Colors.CYAN)}")

        duration = datetime.now() - datetime.fromisoformat(
            self.session_data["start_time"]
        )

        print(
            f"Files downloaded: {config.colorize(self.session_data['files_downloaded'], config.Colors.GREEN)}"
        )
        print(
            f"Files skipped:    {config.colorize(self.session_data['files_skipped'], config.Colors.YELLOW)}"
        )
        print(
            f"Files failed:     {config.colorize(self.session_data['files_failed'], config.Colors.RED)}"
        )
        print(
            f"Total data:       {config.colorize(format_size(self.session_data['total_downloaded']), config.Colors.GREEN)}"
        )
        print(f"Session duration: {str(duration).split('.')[0]}")
        print(f"Download folder:  {self.download_base.absolute()}")
        print(f"{config.colorize('═' * 50, config.Colors.CYAN)}\n")

    def run(self):
        """Main application loop"""
        self.ui.show_message(f"🚀 Starting HTTP Directory Explorer", "info")
        self.ui.show_message(f"Target: {self.base_url}", "info")
        self.ui.show_message(
            f"Download folder: {self.download_base.absolute()}", "info"
        )

        self._load_history()

        while True:
            self._process_directory()


def main():
    """Entry point"""
    try:
        import tqdm
    except ImportError:
        print(f"{config.Colors.RED}Error: tqdm is not installed.{config.Colors.RESET}")
        print(
            f"Install with: {config.Colors.CYAN}pip install tqdm{config.Colors.RESET}"
        )
        sys.exit(1)

    base_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "http://paysites.mustbedestroyed.org/booty/"
    )

    if not base_url.startswith(("http://", "https://")):
        print(
            f"{config.Colors.RED}Error: URL must start with http:// or https://{config.Colors.RESET}"
        )
        sys.exit(1)

    explorer = HTTPExplorer(base_url)
    explorer.run()


if __name__ == "__main__":
    main()
