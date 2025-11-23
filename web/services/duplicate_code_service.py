import hashlib
from typing import List, Dict

from lizard import analyze_file

import services.github_service as github_service

import os
import hashlib
from collections import defaultdict

from models import db
from models.model import *

def _normalize_line(line: str) -> str:
    """
    Normalize a line of code/text:
    - Strip whitespace
    - Collapse multiple spaces
    - Ignore empty lines
    """
    stripped = line.strip()
    if not stripped:
        return ""
    return " ".join(stripped.split())

def _chunk_hash(lines: List[str]) -> str:
    """Compute a hash for a block of normalized lines."""
    text = "\n".join(lines).encode("utf-8")
    return hashlib.sha1(text).hexdigest()


def find_duplicates(owner, name, commit_sha, min_lines: int = 5, window_size: int = 5):
    files = github_service.fetch_files(owner, name, commit_sha)
    seen: Dict[str, List[Dict]] = defaultdict(list)
    duplicates = []

    for filename, code in files:
        lines = [_normalize_line(l) for l in code.splitlines()]
        lines = [l for l in lines if l]  # drop empty after normalization

        for i in range(len(lines) - window_size + 1):
            chunk = lines[i:i+window_size]
            h = _chunk_hash(chunk)
            snippet = "\n".join(chunk)
            seen[h].append({
                "file": filename,
                "start_line": i+1,
                "end_line": i+window_size,
                "snippet": snippet
            })

    # Collect duplicates
    for h, occurrences in seen.items():
        if len(occurrences) > 1:
            duplicates.append({
                "hash": h,
                "occurrences": occurrences,
                "sample": occurrences[0]["snippet"]
            })

    # Sort by impact (length × frequency)
    duplicates.sort(key=lambda d: len(d["sample"].splitlines()) * len(d["occurrences"]), reverse=True)
    return duplicates
        

