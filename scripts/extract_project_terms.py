import os
import re
import json
import sys
import time

# 配置忽略的目录和文件后缀，大幅提升扫描速度
IGNORE_DIRS = {'.git', 'node_modules', 'venv', '.env', '__pycache__', 'dist', 'build', '.cursor'}
VALID_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.md', '.txt', '.json', '.yml', '.yaml'}

def get_project_root():
    # 假设脚本在 .cursor/skills/prompt-corrector/scripts/ 下
    # 项目根目录向上退 4 级
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

def extract_terms_from_text(text):
    terms = set()
    # 匹配 CamelCase (如 UserController, ReactComponent)
    camel_case = re.findall(r'\b[A-Z][a-zA-Z0-9]+\b', text)
    # 匹配 snake_case (如 user_controller, fetch_data)
    snake_case = re.findall(r'\b[a-z]+_[a-z0-9_]+\b', text)
    
    terms.update(camel_case)
    terms.update(snake_case)
    return terms

def scan_project(root_dir):
    project_terms = set()
    file_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 过滤忽略的目录
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            # 1. 提取文件名作为专有名词（去掉后缀）
            base_name = os.path.splitext(filename)[0]
            if len(base_name) > 2:
                project_terms.add(base_name)
            
            # 2. 提取文件内容中的专有名词
            ext = os.path.splitext(filename)[1].lower()
            if ext in VALID_EXTENSIONS:
                filepath = os.path.join(dirpath, filename)
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
    print("Starting fast project indexing...")
    
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
