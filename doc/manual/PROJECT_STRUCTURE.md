# 项目结构

```text
smart-parking-management/
├── .github/workflows/
│   ├── tests.yml                 # 测试与公开包检查
│   └── pages.yml                 # 英文项目页发布
├── backend/
│   ├── ai_engine.py              # 历史基线与规则调度
│   ├── auth.py                   # JWT认证
│   ├── config.py                 # 环境配置
│   ├── database.py               # 数据模型
│   ├── init_data.py              # 明确标注的演示数据
│   ├── main.py                   # FastAPI入口
│   ├── schemas.py                # 输入输出验证
│   ├── security.py               # bcrypt密码哈希
│   └── routers/                  # API路由
├── doc/
│   ├── manual/                   # 当前与历史文档
│   └── product_mgt/              # 七份设计材料（最新为 2026-08 v7）
├── examples/                     # 人工演示脚本
├── frontend/                     # HTML/CSS/JavaScript SPA
├── images/                       # README截图
├── project-intro/                # GitHub英文案例页与Pages演示页
├── scripts/                      # SQLite备份与公开包检查
├── tests/                        # 自动化测试
├── .env.example                  # 非敏感环境变量模板
├── compose.yaml                  # 容器运行与持久化数据卷
├── Dockerfile                    # 应用镜像
├── CONTRIBUTING.md
├── EVIDENCE_AND_LIMITATIONS.md
├── LICENSE
├── MAINTAINER_ROLE.md            # 维护者职责、证据与归属边界
├── PUBLIC_RELEASE.md
├── README.md
├── README_ZH.md
├── REUSE.md
├── SECURITY.md
├── pyproject.toml
└── uv.lock                       # 锁定依赖
```

当前后端把静态前端挂载在根路径，并把 API 路由放在静态挂载之前。业务路由使用统一管理员依赖进行鉴权。
