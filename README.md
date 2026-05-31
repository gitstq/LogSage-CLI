<div align="center">

# 🧙 LogSage-CLI

**Lightweight Terminal Log Intelligence Analysis Engine**

轻量级终端日志智能分析引擎

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Textual](https://img.shields.io/badge/Powered%20by-Textual-purple?style=flat-square)](https://textual.textualize.io/)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**LogSage-CLI** is a powerful, lightweight terminal-based log analysis tool that brings intelligence to your log inspection workflow. Built with modern Python and the Textual TUI framework, it offers an intuitive interface for analyzing log files of any size.

**Key Differentiators:**
- 🧠 **Smart Error Clustering** - Automatically groups similar errors using AI-powered similarity detection
- 📊 **Real-time Visualization** - Interactive histograms and statistics without leaving your terminal
- 🎯 **Zero-dependency Core** - Pure Python with minimal external requirements
- 🔍 **15+ Format Support** - Auto-detects Syslog, Apache, Nginx, JSON, Docker, Kubernetes, and more

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Format Detection** | Automatically identifies 15+ log formats |
| 📊 **Interactive TUI** | Beautiful terminal interface with mouse support |
| 🧠 **Error Clustering** | Groups similar errors for faster debugging |
| 💾 **SQL-like Queries** | Query logs using SQLite virtual tables |
| 📤 **Export Options** | JSON, Markdown, and HTML reports |
| ⌨️ **Vim Keybindings** | Familiar navigation for power users |
| 🗜️ **Compression Support** | Handles .gz files seamlessly |
| 🎨 **Syntax Highlighting** | Color-coded log levels and JSON formatting |

### 🚀 Quick Start

#### Installation

```bash
pip install logsage-cli
```

#### Usage Examples

```bash
# View a single log file
logsage /var/log/syslog

# View multiple files (auto-merged by timestamp)
logsage app.log error.log nginx/access.log

# Analyze gzipped logs
logsage /var/log/nginx/access.log.gz

# Export analysis to JSON
logsage app.log --export json --output report.json

# Generate Markdown report
logsage app.log --export markdown --output report.md
```

### ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate entries |
| `f` | Focus search box |
| `Enter` | Apply filter |
| `e` | Jump to next error |
| `E` | Jump to previous error |
| `r` | Refresh data |
| `c` | Clear filter |
| `s` | Update statistics |
| `d` | Focus detail view |
| `q` or `Ctrl+C` | Quit |
| `?` | Show help |

### 📖 Supported Log Formats

- **Syslog** - Standard system logs
- **Apache/Nginx** - Web server access logs
- **JSON Lines** - Structured JSON logs
- **Docker** - Container logs
- **Kubernetes** - K8s pod logs
- **Logfmt** - Key=value formatted logs
- **Python Traceback** - Exception stack traces
- **Generic Timestamp** - Any timestamp-prefixed logs

### 💡 Design Philosophy

LogSage was designed with three core principles:

1. **Zero Friction** - Install and analyze logs in seconds
2. **Developer First** - Vim bindings, keyboard-driven, terminal-native
3. **Intelligence Built-in** - Smart clustering and pattern detection

### 📦 Building from Source

```bash
git clone https://github.com/gitstq/LogSage-CLI.git
cd LogSage-CLI
pip install -e .
```

### 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**LogSage-CLI** 是一款强大的轻量级终端日志智能分析工具，为您的日志检查工作流带来智能化体验。基于现代 Python 和 Textual TUI 框架构建，它为分析任何大小的日志文件提供了直观的界面。

**核心差异化亮点：**
- 🧠 **智能错误聚类** - 使用 AI 驱动的相似度检测自动分组相似错误
- 📊 **实时可视化** - 无需离开终端即可查看交互式直方图和统计信息
- 🎯 **零依赖核心** - 纯 Python 实现，外部依赖极少
- 🔍 **15+ 格式支持** - 自动识别 Syslog、Apache、Nginx、JSON、Docker、Kubernetes 等格式

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **智能格式识别** | 自动识别 15+ 种日志格式 |
| 📊 **交互式 TUI** | 美观的终端界面，支持鼠标操作 |
| 🧠 **错误聚类** | 将相似错误分组，加速调试 |
| 💾 **类 SQL 查询** | 使用 SQLite 虚拟表查询日志 |
| 📤 **导出选项** | 支持 JSON、Markdown 和 HTML 报告 |
| ⌨️ **Vim 快捷键** | 为高级用户提供熟悉的导航体验 |
| 🗜️ **压缩支持** | 无缝处理 .gz 文件 |
| 🎨 **语法高亮** | 日志级别颜色编码和 JSON 格式化 |

### 🚀 快速开始

#### 安装

```bash
pip install logsage-cli
```

#### 使用示例

```bash
# 查看单个日志文件
logsage /var/log/syslog

# 查看多个文件（按时间戳自动合并）
logsage app.log error.log nginx/access.log

# 分析 gzip 压缩的日志
logsage /var/log/nginx/access.log.gz

# 导出分析结果为 JSON
logsage app.log --export json --output report.json

# 生成 Markdown 报告
logsage app.log --export markdown --output report.md
```

### ⌨️ 键盘快捷键

| 按键 | 功能 |
|------|------|
| `↑/↓` 或 `j/k` | 上下导航 |
| `f` | 聚焦搜索框 |
| `Enter` | 应用筛选 |
| `e` | 跳转到下一个错误 |
| `E` | 跳转到上一个错误 |
| `r` | 刷新数据 |
| `c` | 清除筛选 |
| `s` | 更新统计 |
| `d` | 聚焦详情视图 |
| `q` 或 `Ctrl+C` | 退出 |
| `?` | 显示帮助 |

### 📖 支持的日志格式

- **Syslog** - 标准系统日志
- **Apache/Nginx** - Web 服务器访问日志
- **JSON Lines** - 结构化 JSON 日志
- **Docker** - 容器日志
- **Kubernetes** - K8s Pod 日志
- **Logfmt** - Key=value 格式日志
- **Python Traceback** - 异常堆栈跟踪
- **Generic Timestamp** - 任何带时间戳前缀的日志

### 💡 设计理念

LogSage 遵循三个核心设计原则：

1. **零摩擦** - 数秒内完成安装并开始分析日志
2. **开发者优先** - Vim 绑定、键盘驱动、原生终端体验
3. **内置智能** - 智能聚类和模式检测

### 📦 从源码构建

```bash
git clone https://github.com/gitstq/LogSage-CLI.git
cd LogSage-CLI
pip install -e .
```

### 🧪 运行测试

```bash
pip install pytest
pytest tests/ -v
```

### 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 开源协议

本项目采用 MIT 协议开源 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹