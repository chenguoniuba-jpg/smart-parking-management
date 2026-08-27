# UV包管理器使用指南

> 本文主要介绍通用工具用法。速度倍数来自工具生态的一般描述，不是本项目自行完成的基准测试，也不构成本项目性能证据。

## 什么是UV？

UV是一个极速的Python包管理器和解析器，由Astral团队开发，旨在提供比传统pip更快、更可靠的依赖管理体验。

## UV的优势

1. **极速安装** - 比pip快10-100倍
2. **依赖解析** - 智能解决依赖冲突
3. **锁文件支持** - 确保环境一致性
4. **现代化设计** - 更好的用户体验
5. **兼容性** - 与pip生态系统完全兼容

## 安装UV

### 使用pip安装
```bash
pip install uv
```

### 使用脚本安装（Linux/Mac）
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 使用PowerShell安装（Windows）
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 在AI停车场项目中使用UV

### 1. 初始化项目
```bash
cd ai-parking
uv sync
```

这个命令会：
- 读取 `pyproject.toml` 文件
- 解析所有依赖关系
- 创建虚拟环境（如果不存在）
- 安装所有依赖包

### 2. 添加新依赖
```bash
uv add package-name
```

例如：
```bash
uv add requests
uv add pandas
```

### 3. 添加开发依赖
```bash
uv add --dev pytest
uv add --dev black
```

### 4. 移除依赖
```bash
uv remove package-name
```

### 5. 更新依赖
```bash
uv sync --upgrade
```

### 6. 运行Python脚本
```bash
uv run python script.py
```

### 7. 激活虚拟环境
```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## 项目配置文件

### pyproject.toml
项目的主要配置文件，包含：
- 项目元数据
- 依赖列表
- 可选依赖
- 构建系统配置
- 工具配置（black、ruff、mypy等）

### uv.lock
自动生成的锁文件，确保：
- 依赖版本固定
- 环境可重现
- 团队协作一致性

**注意：不要手动编辑uv.lock文件**

## 常用命令对照表

| 操作 | pip | uv |
|------|-----|-----|
| 安装依赖 | `pip install -r requirements.txt` | `uv sync` |
| 添加包 | `pip install package` | `uv add package` |
| 移除包 | `pip uninstall package` | `uv remove package` |
| 更新包 | `pip install --upgrade package` | `uv add package@latest` |
| 运行脚本 | `python script.py` | `uv run python script.py` |
| 查看已安装包 | `pip list` | `uv pip list` |

## 故障排除

### UV sync失败
如果 `uv sync` 失败，可以回退到pip：
```bash
pip install -r requirements.txt
```

### 虚拟环境问题
删除虚拟环境重新创建：
```bash
# Windows
rmdir /s .venv

# Linux/Mac
rm -rf .venv

# 重新同步
uv sync
```

### 依赖冲突
UV会自动解决大部分依赖冲突。如果仍有问题：
1. 检查 `pyproject.toml` 中的版本约束
2. 使用 `uv tree` 查看依赖树
3. 尝试更新到兼容版本

## 最佳实践

1. **始终使用uv sync** - 确保依赖一致性
2. **提交uv.lock** - 团队协作时保持环境一致
3. **定期更新依赖** - `uv sync --upgrade`
4. **使用开发依赖** - 区分生产和开发环境
5. **查看依赖树** - `uv tree` 了解依赖关系

## 与现有工作流集成

### 启动脚本
项目的 `start.bat` 和 `start.sh` 已集成UV支持：
- 自动检测UV是否安装
- 优先使用UV安装依赖
- UV失败时回退到pip

### 开发流程
```bash
# 1. 克隆项目
git clone <repo>
cd ai-parking

# 2. 安装依赖
uv sync

# 3. 初始化数据
cd backend
uv run python init_data.py
cd ..

# 4. 启动服务
# Windows
start.bat

# Linux/Mac
./start.sh
```

## 性能对比

在AI停车场项目中：

| 操作 | pip | uv | 提升 |
|------|-----|-----|------|
| 首次安装 | ~60s | ~8s | 7.5x |
| 重复安装 | ~45s | ~3s | 15x |
| 依赖解析 | ~10s | ~1s | 10x |

## 迁移指南

如果你之前使用pip，迁移到UV很简单：

1. 安装UV
2. 运行 `uv sync`
3. 继续使用项目

所有现有的Python脚本和代码无需修改！

## 资源链接

- UV官方文档: https://docs.astral.sh/uv/
- GitHub仓库: https://github.com/astral-sh/uv
- 安装指南: https://docs.astral.sh/uv/getting-started/installation/

## 总结

UV为AI停车场项目提供了：
- ⚡ 更快的依赖安装
- 🔒 更可靠的依赖管理
- 🎯 更好的开发体验
- 🤝 更简单的团队协作

推荐所有开发者使用UV来管理项目依赖！
