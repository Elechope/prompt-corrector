import os
import re
import json
import time
import subprocess

# 配置忽略的目录和文件后缀
VALID_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.md', '.txt', '.json', '.yml', '.yaml'}

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

def get_git_tracked_files(root_dir):
    """
    利用 Git 获取所有被追踪的文件，天然支持 .gitignore，
    极大提升大项目的扫描速度，避免扫描 node_modules 等。
    """
    try:
        # 切换到项目根目录执行 git ls-files
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
        print(f"Git ls-files failed (maybe not a git repo). Fallback to os.walk. Error: {e}")
        return None

def extract_terms_from_text(text):
    terms = set()
    camel_case = re.findall(r'\b[A-Z][a-zA-Z0-9]+\b', text)
    snake_case = re.findall(r'\b[a-z]+_[a-z0-9_]+\b', text)
    terms.update(camel_case)
    terms.update(snake_case)
    return terms

def scan_project(root_dir):
    project_terms = set()
    file_count = 0
    
    # 优先使用 Git 获取文件列表（原生支持 .gitignore）
    files_to_scan = get_git_tracked_files(root_dir)
    
    if files_to_scan is None:
        # 降级方案：传统的 os.walk
        IGNORE_DIRS = {'.git', 'node_modules', 'venv', '.env', '__pycache__', 'dist', 'build', '.cursor'}
        files_to_scan = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
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
        if ext in VALID_EXTENSIONS:
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
    print("Starting fast project indexing (Git-aware)...")
    
    root_dir = get_project_root()
    terms, file_count = scan_project(root_dir)
    
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
        with open(dict_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        elapsed = time.time() - start_time
        print(f"Indexing complete in {elapsed:.2f} seconds.")
        print(f"Scanned {file_count} files. Extracted {len(terms)} project terms.")
    except Exception as e:
        print(f"Error saving dictionary: {e}")

if __name__ == "__main__":
    main()
