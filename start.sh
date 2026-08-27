#!/bin/bash

echo "===================================="
echo "智能停车场管理系统启动脚本"
echo "===================================="
echo ""

echo "[1/3] 检查uv包管理器..."
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到uv，请先按照 https://docs.astral.sh/uv/ 安装"
    exit 1
fi

echo ""
echo "[2/3] 安装依赖并初始化演示数据库..."
uv sync
uv run python -m backend.init_data

echo ""
echo "[3/3] 启动服务..."
echo ""
echo "正在启动后端API服务 (端口8000)..."
echo "前端界面: http://localhost:8000 (后端直接渲染)"
echo "API文档: http://localhost:8000/docs"
echo "管理员密码来自ADMIN_PASSWORD；未设置时由初始化脚本一次性生成。"
uv run python -m backend.main
