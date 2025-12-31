#!/usr/bin/env python3
"""
File downloader with tqdm progress bar
"""
import urllib.request
import urllib.error
import urllib.response
from pathlib import Path
from typing import Optional
from tqdm import tqdm
import config
import utils


class FileDownloader:
    """Handles file downloads with progress bar and resume support"""

    def __init__(self, session_data: dict):
        self.session_data = session_data

    def download(self, url: str, local_path: Path) -> bool:
        """Download a file with progress bar and resume support"""
        local_path.parent.mkdir(parents=True, exist_ok=True)

        file_name = local_path.name

        mode, initial_pos, remote_size = self._prepare_download(
            url, local_path, file_name
        )

        if mode is None:
            return True

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": config.CONFIG["user_agent"]}
            )

            if initial_pos > 0:
                req.add_header("Range", f"bytes={initial_pos}-")
                print(
                    f"{config.colorize('⏸️  Resuming:', config.Colors.CYAN)} {file_name} ({utils.format_size(initial_pos)}/{utils.format_size(remote_size)})"
                )

            response = urllib.request.urlopen(
                req, timeout=config.CONFIG["download_timeout"]
            )

            if initial_pos > 0 and response.status != 206:
                print(
                    f"{config.colorize}'⚠️  Server doesn't support resume, starting from beginning:', {config.Colors.YELLOW} {file_name}"
                )
                mode = "wb"
                initial_pos = 0
                req = urllib.request.Request(
                    url, headers={"User-Agent": config.CONFIG["user_agent"]}
                )
                response = urllib.request.urlopen(
                    req, timeout=config.CONFIG["download_timeout"]
                )

            if initial_pos > 0 and response.status == 206:
                content_range = response.headers.get("Content-Range", "")
                if content_range:
                    total_match = content_range.split("/")
                    if len(total_match) > 1:
                        remote_size = int(total_match[1])

            # progress for downloading
            with tqdm(
                total=remote_size,
                initial=initial_pos,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=file_name[:40],
                bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
                leave=False,
            ) as pbar:

                with open(local_path, mode) as f:
                    while True:
                        chunk = response.read(config.CONFIG["chunk_size"])
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))

            # confirming the download
            success = self._verify_download(local_path, remote_size, file_name)
            if success:
                self._update_session_stats(
                    remote_size - initial_pos if initial_pos > 0 else remote_size
                )

            return success

        except urllib.error.HTTPError as e:
            if e.code == 416:
                print(
                    f"{config.colorize('⚠️  Range error, checking file:', config.Colors.YELLOW)} {file_name}"
                )
                if local_path.exists():
                    actual_size = local_path.stat().st_size
                    if actual_size >= remote_size:
                        print(
                            f"{config.colorize('✓ File already complete:', config.Colors.GREEN)} {file_name}"
                        )
                        self.session_data["files_skipped"] += 1
                        return True
                print(
                    f"{config.colorize('↻ Retrying from beginning:', config.Colors.YELLOW)} {file_name}"
                )
                return self._retry_download(url, local_path, file_name)
            else:
                print(
                    f"{config.colorize('✗ HTTP Error:', config.Colors.RED)} {file_name} - {e.code} {e.reason}"
                )
                self.session_data["files_failed"] += 1
                return False

        except Exception as e:
            print(
                f"{config.colorize('✗ Download failed:', config.Colors.RED)} {file_name} - {str(e)}"
            )
            self.session_data["files_failed"] += 1
            return False

    def _prepare_download(self, url: str, local_path: Path, file_name: str) -> tuple:
        """Prepare download - check existing file and get remote size"""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": config.CONFIG["user_agent"]}, method="HEAD"
            )
            with urllib.request.urlopen(
                req, timeout=config.CONFIG["request_timeout"]
            ) as response:
                remote_size = int(response.headers.get("Content-Length", 0))
        except:
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": config.CONFIG["user_agent"]}
                )
                with urllib.request.urlopen(
                    req, timeout=config.CONFIG["request_timeout"]
                ) as response:
                    remote_size = int(response.headers.get("Content-Length", 0))
            except Exception as e:
                print(
                    f"{config.colorize('✗ Cannot get file info:', config.Colors.RED)} {file_name} - {str(e)}"
                )
                return None, 0, 0

        # checking if file is there
        if local_path.exists():
            local_size = local_path.stat().st_size

            if local_size == remote_size and remote_size > 0:
                print(
                    f"{config.colorize('⏭️  Skipped:', config.Colors.YELLOW)} {file_name} "
                    f"(already exists: {utils.format_size(remote_size)})"
                )
                self.session_data["files_skipped"] += 1
                return None, 0, 0

            elif remote_size > 0 and local_size < remote_size:
                return "ab", local_size, remote_size

            else:
                print(
                    f"{config.colorize('↻ Overwriting:', config.Colors.YELLOW)} {file_name}"
                )
                return "wb", 0, remote_size

        # new
        return "wb", 0, remote_size

    def _retry_download(self, url: str, local_path: Path, file_name: str) -> bool:
        """Retry download from beginning"""
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": config.CONFIG["user_agent"]}
            )

            with urllib.request.urlopen(
                req, timeout=config.CONFIG["download_timeout"]
            ) as response:
                remote_size = int(response.headers.get("Content-Length", 0))

                with tqdm(
                    total=remote_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=file_name[:40],
                    bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
                    leave=False,
                ) as pbar:

                    with open(local_path, "wb") as f:
                        while True:
                            chunk = response.read(config.CONFIG["chunk_size"])
                            if not chunk:
                                break
                            f.write(chunk)
                            pbar.update(len(chunk))

                success = self._verify_download(local_path, remote_size, file_name)
                if success:
                    self._update_session_stats(remote_size)
                return success

        except Exception as e:
            print(
                f"{config.colorize('✗ Retry failed:', config.Colors.RED)} {file_name} - {str(e)}"
            )
            self.session_data["files_failed"] += 1
            return False

    def _verify_download(
        self, local_path: Path, expected_size: int, file_name: str
    ) -> bool:
        """Verify downloaded file size"""
        if expected_size > 0:
            actual_size = local_path.stat().st_size
            if actual_size != expected_size:
                print(
                    f"{config.colorize('✗ Size mismatch:', config.Colors.RED)} "
                    f"{file_name} - Expected {utils.format_size(expected_size)}, "
                    f"got {utils.format_size(actual_size)}"
                )
                self.session_data["files_failed"] += 1
                return False

        print(
            f"{config.colorize('✓ Downloaded:', config.Colors.GREEN)} {file_name} "
            f"({utils.format_size(expected_size)})"
        )
        return True

    def _update_session_stats(self, downloaded_bytes: int):
        """Update session statistics"""
        self.session_data["total_downloaded"] += downloaded_bytes
        self.session_data["files_downloaded"] += 1
