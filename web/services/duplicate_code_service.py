import hashlib
from typing import List, Dict

from lizard import analyze_file

import services.github_service as github_service

from models import db
from models.model import *

def _normalize_function_body(code: str, start_line: int, end_line: int) -> str:
    """Extract and normalize function body for comparison.
    
    Args:
        code: Full file source code
        start_line: Function start line (1-indexed)
        end_line: Function end line (1-indexed)
    
    Returns:
        Normalized function body (whitespace-collapsed, comments removed)
    """
    lines = code.splitlines()
    # Extract function lines (convert to 0-indexed)
    func_lines = lines[start_line - 1:end_line]
    
    normalized = []
    for line in func_lines:
        stripped = line.strip()
        # Skip blank lines and comments
        if not stripped or stripped.startswith('#'):
            continue
        # Skip docstrings (simple detection)
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        # Collapse whitespace
        normalized.append(' '.join(stripped.split()))
    
    return '\n'.join(normalized)


def find_duplicates(owner: str, name: str, branch: str, commit_sha: str, min_lines: int = 6) -> List[Dict]:
    """
    Find duplicated code blocks (functions) across Python files using Lizard.

    Returns a list of dicts:
      {
        'hash': <function-body-hash>,
        'length': <lines in function>,
        'occurrences': [
            {'file': 'path', 'function': 'func_name', 'start_line': 42, 'end_line': 48}, ...
        ],
        'sample': 'normalized function body'
      }

    Uses Lizard to parse functions and compares their normalized bodies.
    """
    files = github_service.fetch_files(owner, name, commit_sha)

    # Parse all functions from all files using Lizard
    all_functions = []
    
    for filename, code in files:
        try:
            analysis = analyze_file.analyze_source_code(filename, code)
            for func in analysis.function_list:
                # Calculate function length (end_line - start_line)
                func_length = func.end_line - func.start_line + 1
                
                # Skip very short functions
                if func_length < min_lines:
                    continue
                
                # Normalize the function body for comparison
                normalized_body = _normalize_function_body(code, func.start_line, func.end_line)
                
                # Skip if normalized body is too short
                if len(normalized_body.strip()) < 20:
                    continue
                
                # Compute hash of normalized body
                body_hash = hashlib.sha1(normalized_body.encode('utf-8')).hexdigest()
                
                all_functions.append({
                    'file': filename,
                    'function': func.name,
                    'start_line': func.start_line,
                    'end_line': func.end_line,
                    'length': func_length,
                    'body_hash': body_hash,
                    'normalized_body': normalized_body
                })
        except Exception as e:
            # Skip files that Lizard can't parse
            print(f"Warning: Could not analyze {filename}: {e}")
            continue
    
    # Group functions by their body hash (duplicates have same hash)
    hash_groups = {}
    for func_info in all_functions:
        h = func_info['body_hash']
        if h not in hash_groups:
            hash_groups[h] = []
        hash_groups[h].append(func_info)
    
    # Build duplicate report (only groups with 2+ occurrences)
    duplicates = []
    for body_hash, group in hash_groups.items():
        if len(group) < 2:
            continue
        
        occurrences = [
            {
                'file': func['file'],
                'function': func['function'],
                'start_line': func['start_line'],
                'end_line': func['end_line']
            }
            for func in group
        ]
        
        # Use the first function's info as representative
        representative = group[0]
        
        duplicates.append({
            'hash': body_hash,
            'length': representative['length'],
            'occurrences': occurrences,
            'sample': representative['normalized_body']
        })
    
    # Sort by impact (length * number of occurrences)
    duplicates.sort(key=lambda x: x['length'] * len(x['occurrences']), reverse=True)
    
    return duplicates