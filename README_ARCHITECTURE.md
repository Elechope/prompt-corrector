# 微服务化架构设计方案

基于您的需求，我们将 `prompt-corrector` 从一个本地 IDE 脚本集合，升级为一个标准的、兼容 OpenClaw 的 FastAPI 微服务插件。

## 改造后的目录结构设计

```text
prompt-corrector/
├── openclaw-manifest.json            # OpenClaw 插件清单 (定义 API 路由和元数据)
├── SOUL.md                           # OpenClaw 智能体系统提示词 (替代 SKILL.md)
├── server.py                         # FastAPI 应用入口
├── requirements.txt                  # 依赖清单 (fastapi, uvicorn, sqlalchemy 等)
├── config.json                       # 扫描策略与全局配置
├── app/                              # 微服务核心代码包
│   ├── __init__.py
│   ├── api/                          # 路由层 (Controllers)
│   │   ├── __init__.py
│   │   └── endpoints.py              # /api/v1/filter, /api/v1/whitelist, /api/v1/scan
│   ├── core/                         # 核心配置与数据库连接
│   │   ├── __init__.py
│   │   └── database.py               # SQLAlchemy 引擎与 Session 管理
│   ├── models/                       # 数据模型层
│   │   ├── __init__.py
│   │   └── dictionary.py             # SQLite 表结构 (Whitelist, ProjectTerm)
│   └── services/                     # 业务逻辑层 (复用原脚本核心逻辑)
│       ├── __init__.py
│       ├── filter_service.py         # 原 pre_filter.py 逻辑
│       ├── whitelist_service.py      # 原 add_to_whitelist.py 逻辑
│       └── scanner_service.py        # 原 extract_project_terms.py 逻辑
└── assets/
    └── dictionary.db                 # SQLite 数据库文件 (运行时自动生成)
```

## 设计亮点说明

1. **分层架构 (MVC/三层架构)**：将路由 (`api`)、业务逻辑 (`services`) 和数据模型 (`models`) 严格分离，符合现代 Python 后端开发规范。
2. **SQLAlchemy ORM**：使用 SQLAlchemy 管理 SQLite，自带连接池和并发锁机制，彻底解决多端并发写入的安全问题。
3. **BackgroundTasks**：在 `endpoints.py` 中，扫描任务 (`/api/v1/scan`) 将利用 FastAPI 的 `BackgroundTasks` 异步执行，接口瞬间返回 `202 Accepted`，绝不阻塞主线程。
4. **OpenClaw 生态融合**：`openclaw-manifest.json` 将作为服务发现的凭证，而 `SOUL.md` 将指导 Agent 如何通过 HTTP 请求与这个微服务交互。

