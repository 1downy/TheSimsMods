#!/usr/bin/env python3
"""
HTML Parser for AutoIndex directory listings using BeautifulSoup
"""
from typing import Dict, List
from bs4 import BeautifulSoup
import utils


class AutoIndexParser:
    """Parser for AutoIndex directory listings using BeautifulSoup"""

    def __init__(self):
        pass

    def parse(self, html: str) -> List[Dict]:
        """Parse AutoIndex directory listing HTML using BeautifulSoup"""
        soup = BeautifulSoup(html, "html.parser")
        items = []

        # print("DEBUG: HTML length:", len(html))
        # print("DEBUG: First 500 chars:", html[:500])

        tables = soup.find_all("table")
        # print(f"DEBUG: Found {len(tables)} tables")

        for i, table in enumerate(tables):
            table_id = table.get("id", "no-id")
            # print(f"DEBUG: Table {i} id: {table_id}")

            rows = table.find_all("tr")
            # print(f"DEBUG: Table {i} has {len(rows)} rows")
            if len(rows) > 1:
                for row in rows:
                    item = self._parse_row(row)
                    if item:
                        items.append(item)
                break

        if not items:
            # print("DEBUG: No items found in tables, trying broader search...")
            all_rows = soup.find_all("tr")
            for row in all_rows:
                item = self._parse_row(row)
                if item and item not in items:
                    items.append(item)

        # print(f"DEBUG: Total items parsed: {len(items)}")
        # for item in items:
        #     print(f"  - {item['name']} ({'DIR' if item['is_directory'] else 'FILE'}): {item['href']}")
        return sorted(items, key=lambda x: (not x["is_directory"], x["name"].lower()))

    def _parse_row(self, row) -> Dict:
        """Parse a single table row"""
        if row.find("th"):
            return None

        cells = row.find_all("td")
        if len(cells) < 3:
            return None
        first_cell = cells[0]
        link = first_cell.find("a")
        if not link:
            return None

        href = link.get("href", "").strip()
        name = link.get_text(" ", strip=True)
        name = utils.clean_name(name)

        if (
            not name
            or name.lower() in ["parent directory", "up", ".."]
            or "icon" in name.lower()
        ):
            return None

        last_modified = cells[1].get_text(" ", strip=True)
        size = cells[2].get_text(" ", strip=True)

        is_directory = (
            href.endswith("/")
            or size == "-"
            or "folder" in str(first_cell).lower()
            or any(
                "folder" in str(img.get("alt", "")).lower()
                for img in first_cell.find_all("img")
            )
        )

        return {
            "href": href,
            "name": name,
            "last_modified": last_modified,
            "size": size,
            "is_directory": is_directory,
            "is_file": not is_directory
            and size != "-"
            and size != ""
            and size.lower() != "none",
        }
