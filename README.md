# 🧙 LogSage-CLI

> **Lightweight Terminal Log Intelligence Analysis Engine**  
> 轻量级终端日志智能分析引擎

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Textual](https://img.shields.io/badge/Powered%20by-Textual-purple)](https://textual.textualize.io/)

---

## 🌟 Features

- 🔍 **Smart Format Detection** - Auto-detects 15+ log formats (Syslog, Apache, Nginx, JSON, logfmt, etc.)
- 📊 **Real-time Visualization** - Interactive TUI with histograms and statistics
- 🧠 **Intelligent Analysis** - Error clustering and pattern recognition
- 💾 **SQL-like Queries** - Query logs using SQLite virtual tables
- 📤 **Multiple Exports** - JSON, Markdown, HTML report generation
- ⌨️ **Vim Keybindings** - Familiar navigation experience
- 🗜️ **Compression Support** - Handle gzip (.gz) files seamlessly
- 🎯 **Zero Dependencies Core** - Pure Python with minimal requirements

---

## 🚀 Quick Start

### Installation

```bash
pip install logsage-cli
```

### Usage

```bash
# View a single log file
logsage /var/log/syslog

# View multiple files (merged by timestamp)
logsage app.log error.log

# View gzipped logs
logsage /var/log/nginx/access.log.gz

# Export to JSON
logsage app.log --export json --output report.json

# Export to Markdown
logsage app.log --export markdown --output report.md
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate entries |
| `f` | Focus search box |
| `e` | Jump to next error |
| `E` | Jump to previous error |
| `r` | Refresh data |
| `c` | Clear filter |
| `q` | Quit |
| `?` | Show help |

---

## 📖 Documentation

See [docs/](docs/) for detailed documentation.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Built with [Textual](https://textual.textualize.io/) - The Python TUI framework
- Inspired by [lnav](https://lnav.org/) - The Log File Navigator
