import subprocess
import tempfile
import os
import json
import re


def analyze_comments_with_semgrep(code_content, filename):
    """
    Analyze code for TODO and FIXME comments using Semgrep
    Returns list of tuples: (entity_type, line_number)
    """
    # Create temporary file for code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as code_file:
        code_file.write(code_content)
        code_file_path = code_file.name

    try:
        # Use the actual YML config file - adjust path as needed
        config_file_path = '/app/semgrep_rules.yml'

        print(f"[semgrep] scanning: {filename}")  # ⬅️ start

        # Run semgrep with the config file
        result = subprocess.run([
            'semgrep', '--config', config_file_path, 
            '--json', code_file_path  
        ], capture_output=True, text=True, timeout=30)
        
        
                
        
        entities_found = []
        
        if result.returncode == 0:
            try:


                output = json.loads(result.stdout)
                for r in output.get("results", []):
                    msg = r.get("extra", {}).get("message", "") or ""
                    snip = r.get("extra", {}).get("lines", "") or ""
                    line = r.get("start", {}).get("line", 0)
                    hay = f"{msg}\n{snip}".upper()
                if "TODO" in hay:
                    print(f"[semgrep] ✓ TODO @ line {line}: {snip.strip()[:120]}")
                    entities_found.append(("TODO", line))
                elif "FIXME" in hay:
                    print(f"[semgrep] ✓ FIXME @ line {line}: {snip.strip()[:120]}")
                    entities_found.append(("FIXME", line))




                for result_item in output.get('results', []):
                    line_number = result_item.get('start', {}).get('line', 1)
                    extra = result_item.get('extra', {})
                    lines = extra.get('lines', '')
                    
                    snippet = lines.strip().splitlines()[0] if lines else ""
                    print(f"[semgrep]  -> line {line_number}: {snippet}")

                    # Determine if it's TODO or FIXME
                    if re.search(r'\bTODO\b', lines, re.IGNORECASE):
                        entities_found.append(('TODO', line_number))
                    elif re.search(r'\bFIXME\b', lines, re.IGNORECASE):
                        entities_found.append(('FIXME', line_number))
                        
            except json.JSONDecodeError:
                print("Failed to parse Semgrep output")
        
        print(f"[semgrep] TODO/FIXME in {filename}: {entities_found}") 
        return entities_found
        
    except subprocess.TimeoutExpired:
        print(f"Semgrep timeout for file {filename}")
        return []
    except Exception as e:
        print(f"Semgrep error for file {filename}: {e}")
        return []
    finally:
        # Clean up temporary file
        try:
            os.unlink(code_file_path)
        except:
            pass