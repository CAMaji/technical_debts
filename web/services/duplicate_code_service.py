import hashlib


import services.github_service as github_service

from models import db
from models.model import *


import hashlib

import services.github_service as github_service

from models import db
from models.model import *


import hashlib
from collections import defaultdict
from typing import Dict, List, Tuple

import services.github_service as github_service

from models import db  # kept in case used elsewhere
from models.model import *  # kept in case used elsewhere


def _hash_block(lines: List[str]) -> str:
    """Hash a normalized list of lines."""
    normalized = "\n".join(line.rstrip() for line in lines)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def _merge_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping or adjacent [start, end] (1‑based, inclusive) ranges."""
    if not ranges:
        return []
    ranges = sorted(ranges, key=lambda r: r[0])
    merged = []
    cur_start, cur_end = ranges[0]
    for s, e in ranges[1:]:
        if s <= cur_end + 1:
            cur_end = max(cur_end, e)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = s, e
    merged.append((cur_start, cur_end))
    return merged


def find_duplicates(owner: str, name: str, commit_sha: str, min_lines: int = 5) -> Dict:
    """
    Find duplicated code blocks across Python files of a given commit.

    - A base block is exactly `min_lines` consecutive lines.
    - We first detect all such duplicated windows via hashing.
    - For each file, overlapping/adjacent windows are merged into larger blocks.
    - Finally, blocks with the same full text that appear 2+ times are reported.
    """
    files = github_service.fetch_files(owner, name, commit_sha)  # [(path, code), ...]

    # 1) Detect duplicated windows of size `min_lines`
    window_map: Dict[str, List[Dict]] = defaultdict(list)
    file_lines: Dict[str, List[str]] = {}

    for path, content in files:
        if not content:
            continue
        lines = content.splitlines()
        file_lines[path] = lines

        if len(lines) < min_lines:
            continue

        for i in range(0, len(lines) - min_lines + 1):
            window = lines[i : i + min_lines]
            h = _hash_block(window)
            window_map[h].append(
                {
                    "path": path,
                    "start_line": i + 1,
                    "end_line": i + min_lines,
                }
            )

    # Keep only hashes that have 2+ occurrences anywhere
    duplicated_windows = {
        h: occs for h, occs in window_map.items() if len(occs) > 1
    }
    if not duplicated_windows:
        return {
            "owner": owner,
            "repo": name,
            "commit": commit_sha,
            "total_duplicates": 0,
            "duplicates": {},
            "min_lines": min_lines,
        }

    # 2) For each file, merge overlapping/adjacent windows into larger ranges
    per_file_ranges: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    for occs in duplicated_windows.values():
        for occ in occs:
            per_file_ranges[occ["path"]].append(
                (occ["start_line"], occ["end_line"])
            )

    merged_blocks_by_path: Dict[str, List[Tuple[int, int]]] = {}
    for path, ranges in per_file_ranges.items():
        merged_blocks_by_path[path] = _merge_ranges(ranges)

    # 3) Group merged blocks by full‑block content hash
    block_map: Dict[str, List[Dict]] = defaultdict(list)

    for path, blocks in merged_blocks_by_path.items():
        lines = file_lines.get(path, [])
        for start_line, end_line in blocks:
            if start_line < 1 or end_line > len(lines) or start_line > end_line:
                continue
            block_lines = lines[start_line - 1 : end_line]
            # Ignore very small blocks (paranoia; should already be >= min_lines)
            if len(block_lines) < min_lines:
                continue

            code = "\n".join(line.rstrip() for line in block_lines)
            full_hash = _hash_block(block_lines)
            block_map[full_hash].append(
                {
                    "file": path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": code,
                }
            )

    # 4) Keep only hashes with 2+ occurrences (real duplicates)
    duplicates: Dict[str, List[Dict]] = {
        h: occs for h, occs in block_map.items() if len(occs) > 1
    }

    return {
        "owner": owner,
        "repo": name,
        "commit": commit_sha,
        "total_duplicates": len(duplicates),
        "duplicates": duplicates,
        "min_lines": min_lines,
    }


def format_duplicates_json(duplicates_result: Dict) -> Dict:
    """Convert duplicates result to a compact JSON‑friendly structure."""
    formatted_duplicates = []

    for block_hash, locations in duplicates_result["duplicates"].items():
        duplicate_group = {
            "hash": block_hash,
            "occurrences": [
                {
                    "index": idx,
                    "file": loc["file"],
                    "start_line": loc["start_line"],
                    "end_line": loc["end_line"],
                    "snippet": loc["code"],
                }
                for idx, loc in enumerate(locations)
            ],
            "sample": locations[0]["code"][:200] if locations else "",
        }
        formatted_duplicates.append(duplicate_group)

    return {
        "repository": {
            "owner": duplicates_result["owner"],
            "name": duplicates_result["repo"],
            "commit": duplicates_result["commit"],
        },
        "analysis": {
            "min_lines": duplicates_result["min_lines"],
            "total_duplicate_groups": duplicates_result["total_duplicates"],
        },
        "duplicates": formatted_duplicates,
    }