import sys
import json
import os
import tempfile

def atomic_write_json(data, filepath):
    """
    Safely write JSON data using a temporary file and atomic rename.
    Prevents file corruption during concurrent access by multiple agents.
    """
    dir_name = os.path.dirname(filepath)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix="tmp_dict_", suffix=".json")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, filepath)
    except Exception as e:
        os.remove(tmp_path)
        raise e

def main():
    # Read word from stdin to prevent Shell Injection
    new_word = sys.stdin.read().strip()
    
    if not new_word:
        print(json.dumps({"status": "ERROR", "message": "No word provided"}))
        return

    dict_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'user_dictionary.json')
    
    # Load existing dictionary
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {"whitelist": [], "project_terms": []}

    if "whitelist" not in data:
        data["whitelist"] = []

    # Add word if not exists
    if new_word not in data["whitelist"]:
        data["whitelist"].append(new_word)
        
        # Save back to file using atomic write
        try:
            atomic_write_json(data, dict_path)
            print(json.dumps({"status": "SUCCESS", "message": f"Successfully added '{new_word}' to whitelist."}))
        except Exception as e:
            print(json.dumps({"status": "ERROR", "message": str(e)}))
    else:
        print(json.dumps({"status": "SKIPPED", "message": f"'{new_word}' is already in the whitelist."}))

if __name__ == "__main__":
    main()
