import os
import re
import json
import time
import subprocess
import tempfile

def get_config():
    """Load configuration for scanning extensions and ignored directories."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # Fallback default configuration
        return {
            "ignore_dirs": [".git", "node_modules", "venv", ".env", "__pycache__", "dist", "build", ".cursor"],
            "valid_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".md", ".txt", ".json", ".yml", ".yaml"]
        }

def get_project_root():
    """
    Dynamically resolve project root by looking for common root markers.
    This makes the script robust across different VM/Container environments.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    markers = ['.git', 'package.json', 'pyproject.toml', 'pom.xml', 'go.mod', 'requirements.txt']
    
    # Traverse upwards until a marker is found or filesystem root is reached
    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
        
    # Fallback to current working directory if no marker is found
    return os.getcwd()

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

def get_git_tracked_files(root_dir):
    """
    利用 Git 获取所有被追踪的文件，天然支持 .gitignore，
    极大提升大项目的扫描速度，避免扫描 node_modules 等。
    """
    try:
        result = subprocess.run(
            ['git', 'ls-files'], 
            cwd=root_dir, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=True
        )
        files = result.stdout.splitlines()
        return [os.path.join(root_dir, f) for f in files]
    except Exception as e:
        print(f"Git ls-files failed. Fallback to os.walk. Error: {e}")
        return None

def extract_terms_from_text(text):
    terms = set()
    camel_case = re.findall(r'\b[A-Z][a-zA-Z0-9]+\b', text)
    snake_case = re.findall(r'\b[a-z]+_[a-z0-9_]+\b', text)
    terms.update(camel_case)
    terms.update(snake_case)
    return terms

def scan_project(root_dir, config):
    project_terms = set()
    file_count = 0
    valid_exts = set(config.get("valid_extensions", []))
    ignore_dirs = set(config.get("ignore_dirs", []))
    
    # 优先使用 Git 获取文件列表（原生支持 .gitignore）
    files_to_scan = get_git_tracked_files(root_dir)
    
    if files_to_scan is None:
        # 降级方案：传统的 os.walk
        files_to_scan = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for filename in filenames:
                files_to_scan.append(os.path.join(dirpath, filename))
                
    for filepath in files_to_scan:
        filename = os.path.basename(filepath)
        
        # 1. 提取文件名作为专有名词
        base_name = os.path.splitext(filename)[0]
        if len(base_name) > 2:
            project_terms.add(base_name)
        
        # 2. 提取文件内容中的专有名词
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_exts:
            try:
                # 限制读取大小，防止读取超大文件卡死（最大 500KB）
                if os.path.getsize(filepath) < 500 * 1024:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        terms = extract_terms_from_text(content)
                        project_terms.update(terms)
                        file_count += 1
            except Exception:
                pass
                    
    return list(project_terms), file_count

def main():
    start_time = time.time()
    print("Starting enterprise-grade project indexing...")
    
    config = get_config()
    root_dir = get_project_root()
    terms, file_count = scan_project(root_dir, config)
    
    # 过滤掉太短的词或纯数字
    terms = [t for t in terms if len(t) > 2 and not t.isdigit()]
    
    # 更新字典
    dict_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'user_dictionary.json')
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {"whitelist": [], "project_terms": []}
        
    data["project_terms"] = sorted(list(set(terms))) # 去重并排序
    
    try:
        atomic_write_json(data, dict_path)
        elapsed = time.time() - start_time
        print(f"Indexing complete in {elapsed:.2f} seconds.")
        print(f"Scanned {file_count} files in {root_dir}. Extracted {len(terms)} project terms.")
    except Exception as e:
        print(f"Error saving dictionary: {e}")

if __name__ == "__main__":
    main()
