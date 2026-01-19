import urllib.request
import json
import re
import sys
import os

# --- CONFIGURATION ---
# UPDATE THIS TAG to the release you want to compare against
REPO_API_URL = "https://api.github.com/repos/am32-firmware/AM32/releases/tags/v2.20"
TARGETS_FILE = "Inc/targets.h"

def get_gh_targets():
    """
    Fetches official artifacts and returns a set of 'Clean Names'
    Example: AM32_NEUTRON_2_6S_AIO_F421_2.20.hex -> NEUTRON_2_6S_AIO_F421
    """
    print(f"Fetching release info from: {REPO_API_URL}")
    try:
        with urllib.request.urlopen(REPO_API_URL) as url:
            data = json.loads(url.read().decode())
            
        assets = data.get("assets", [])
        gh_targets = set()
        
        # Regex matches version suffix: _2.20.hex, _2.20_F421.hex, etc.
        # It looks for an underscore, followed by digits/dots, ending in .hex
        version_suffix_re = re.compile(r"_v?\d+\.\d+\.hex$", re.IGNORECASE)

        for asset in assets:
            name = asset["name"]
            if not name.endswith(".hex"):
                continue

            # 1. Remove AM32_ prefix
            clean = name
            if clean.startswith("AM32_"):
                clean = clean[5:]

            # 2. Remove Version Suffix
            # "NEUTRON_2_6S_AIO_F421_2.20.hex" -> "NEUTRON_2_6S_AIO_F421"
            clean = version_suffix_re.sub("", clean)
            
            gh_targets.add(clean.upper())

        print(f"Found {len(gh_targets)} targets on GitHub.")
        return gh_targets

    except Exception as e:
        print(f"Error fetching GitHub data: {e}")
        sys.exit(1)

def get_local_skip_candidates(gh_targets):
    """
    Parses targets.h to find #ifdef TARGET -> #define FILE_NAME relation.
    If TARGET is not in gh_targets, returns FILE_NAME.
    """
    if not os.path.exists(TARGETS_FILE):
        print(f"Error: {TARGETS_FILE} not found.")
        sys.exit(1)

    skip_list = []
    
    # State tracking
    current_ifdef = None
    
    # Regex to catch #ifdef DEFINITION
    re_ifdef = re.compile(r"^\s*#ifdef\s+(\w+)")
    # Regex to catch #define FILE_NAME "STRING"
    re_filename = re.compile(r'^\s*#define\s+FILE_NAME\s+"([^"]+)"')
    # Regex for #endif (to clear state)
    re_endif = re.compile(r"^\s*#endif")

    with open(TARGETS_FILE, 'r') as f:
        for line in f:
            # 1. Check for #ifdef start
            m_if = re_ifdef.search(line)
            if m_if:
                current_ifdef = m_if.group(1).upper()
                continue

            # 2. Check for FILE_NAME inside the block
            m_file = re_filename.search(line)
            if m_file and current_ifdef:
                file_name_str = m_file.group(1).strip()
                
                # --- COMPARISON LOGIC ---
                # We check if the IFDEF Name (e.g. NEUTRON_2_6S_AIO_F421) exists on GitHub
                if current_ifdef not in gh_targets:
                    # It's NOT on GitHub, so we should SKIP it locally.
                    # We add the FILE_NAME string because that's what CMake uses.
                    skip_list.append(file_name_str)
                
                # Reset matches to prevent duplicates if file is messy
                current_ifdef = None 

            # 3. Clear state on endif (optional, but good for safety)
            if re_endif.search(line):
                current_ifdef = None

    return sorted(list(set(skip_list)))

def main():
    # 1. Get Official List (The "Keep" List)
    gh_targets = get_gh_targets()
    
    # 2. Generate Skip List (Local items NOT in Official List)
    skip_list = get_local_skip_candidates(gh_targets)
    
    # 3. Output
    print("\n" + "="*50)
    print(f"GENERATED SKIP LIST ({len(skip_list)} items)")
    print("="*50)
    print("set(TARGET_RELEASE_SKIP_LIST")
    for item in skip_list:
        print(f'    "{item}"')
    print(")")
    print("="*50)

if __name__ == "__main__":
    main()