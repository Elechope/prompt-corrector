import sys
import json
import os

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "NEEDS_LLM", "reason": "No prompt provided"}))
        return

    prompt = sys.argv[1].strip()
    
    # Load User Dictionary
    dict_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'user_dictionary.json')
    whitelist = []
    if os.path.exists(dict_path):
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                whitelist = json.load(f).get("whitelist", [])
        except Exception:
            pass

    # 1. Fast Pass: If the prompt is exactly a whitelisted word, skip LLM check
    if prompt in whitelist:
        print(json.dumps({"status": "PASS", "message": "Exact whitelist match."}))
        return
        
    # 2. Fast Pass: If the prompt is extremely short (e.g., "ok", "yes", "1"), skip LLM check
    if len(prompt) <= 2 and prompt.isascii():
        print(json.dumps({"status": "PASS", "message": "Short generic confirmation."}))
        return

    # Default: Fallback to LLM for deep semantic check
    print(json.dumps({"status": "NEEDS_LLM", "message": "Requires deep semantic analysis."}))

if __name__ == "__main__":
    main()
