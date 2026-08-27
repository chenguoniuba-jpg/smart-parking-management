# 快速启动

## 环境

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

## 安装

```bash
cp .env.example .env
uv sync --frozen --extra dev
```

复制后请修改 `.env` 中的 `SECRET_KEY` 和 `ADMIN_PASSWORD`，且不要提交 `.env`。

## 初始化演示数据库

```bash
uv run --env-file .env python -m backend.init_data
```

未设置 `ADMIN_PASSWORD` 时，终端会显示一次性生成的管理员密码。所有初始化记录均为演示数据。

也可以指定自己的密码：

```bash
ADMIN_PASSWORD='choose-a-strong-password' uv run python -m backend.init_data
```

## 启动

```bash
uv run --env-file .env python -m backend.main
```

- 前端：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

服务默认只监听本机。生产环境必须设置 `APP_ENV=production`、强 `SECRET_KEY` 和精确的 `CORS_ORIGINS`。

## 测试

```bash
uv run pytest
uv run ruff check --select F821,F822,F823 backend tests scripts
uv run python scripts/check_public_package.py
```

`tests/` 是自动化测试；`examples/` 是需要运行中服务的人工演示脚本，两者用途不同。

Docker 启动、SQLite 备份、健康检查和现场集成边界见根目录 [复用与运维指南](../../REUSE.md)。
