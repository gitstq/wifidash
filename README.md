<div align="center">

# 📡 WiFiDash

**智能WiFi网络诊断与可视化工具**
**Smart WiFi Network Diagnostics & Visualization Tool**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()
[![TUI](https://img.shields.io/badge/TUI-Textual-orange.svg)](https://textual.textualize.io/)

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

WiFiDash 是一款智能WiFi网络诊断与可视化工具，帮助用户快速了解周围的WiFi环境，优化网络配置，提升上网体验。

**灵感来源**：在日常开发和办公中，经常遇到WiFi信号不稳定、信道拥堵等问题。市面上虽然有一些WiFi分析工具，但要么功能复杂难用，要么需要付费。WiFiDash 旨在提供一个**简洁、高效、开源**的替代方案。

**自研差异化亮点**：
- 🎨 美观的TUI界面，无需浏览器即可使用
- 📊 实时信道分析和拥堵检测
- 💡 智能优化建议（最佳信道推荐、安全提醒）
- 🔧 支持CLI和TUI两种使用模式
- 📤 一键导出扫描结果

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📶 **网络扫描** | 扫描周围所有WiFi网络，显示SSID、信号强度、加密方式等 |
| 📊 **信道分析** | 分析2.4GHz和5GHz信道使用情况，检测拥堵 |
| 💡 **智能建议** | 自动推荐最佳信道，检测安全漏洞 |
| 🖥️ **交互式TUI** | 基于Textual的美观终端界面 |
| ⌨️ **CLI支持** | 支持命令行操作，方便脚本集成 |
| 📤 **数据导出** | 支持JSON格式导出，便于后续分析 |
| 🔒 **安全检测** | 自动识别开放网络、WEP等不安全加密 |

### 🚀 快速开始

#### 环境要求

- Python 3.8+
- Linux/macOS/Windows
- 可选：WiFi网卡（用于真实扫描，否则使用演示数据）

#### 安装

```bash
# 从PyPI安装（推荐）
pip install wifidash

# 或从源码安装
git clone https://github.com/gitstq/wifidash.git
cd wifidash
pip install -e .
```

#### 启动TUI界面

```bash
wifidash
```

#### CLI命令

```bash
# 扫描WiFi网络
wifidash scan

# 以JSON格式输出
wifidash scan --json

# 导出到文件
wifidash scan --export results.json

# 分析信道
wifidash channels

# 获取优化建议
wifidash recommend

# 持续监控模式
wifidash monitor --interval 5
```

### 📖 详细使用指南

#### TUI界面操作

| 快捷键 | 功能 |
|--------|------|
| `r` | 刷新扫描 |
| `a` | 切换自动扫描 |
| `e` | 导出数据 |
| `q` | 退出 |
| `?` | 显示帮助 |

#### 信号强度解读

| 信号强度 | 质量 | 说明 |
|----------|------|------|
| -30 ~ -50 dBm | 🟢 优秀 | 信号很强，适合高清视频、游戏 |
| -50 ~ -65 dBm | 🟡 良好 | 信号良好，日常使用无压力 |
| -65 ~ -75 dBm | 🟠 一般 | 信号一般，可能有延迟 |
| -75 dBm以下 | 🔴 较差 | 信号弱，建议调整位置 |

#### 信道选择建议

**2.4GHz频段**：
- 推荐信道：1、6、11（互不干扰）
- 避免使用：2-5、7-10（信道重叠）

**5GHz频段**：
- 推荐信道：36、40、44、48、149、153、157、161
- 干扰较少，适合高速传输

### 💡 设计思路与迭代规划

#### 技术选型原因

- **Python**：跨平台、生态丰富、易于维护
- **Textual**：现代化TUI框架，支持CSS样式、动画效果
- **Rich**：美观的终端输出，支持表格、进度条等

#### 后续功能迭代计划

- [ ] 支持更多WiFi网卡驱动
- [ ] 添加历史数据趋势图
- [ ] 支持WiFi 6E (6GHz) 分析
- [ ] 添加网络速度测试功能
- [ ] 支持导出PDF报告

#### 社区贡献方向

- 欢迎提交Issue和PR
- 支持更多语言的本地化
- 改进扫描算法和准确性

### 📦 打包与部署指南

#### 构建安装包

```bash
# 安装构建依赖
pip install build twine

# 构建
make build

# 上传到PyPI
make upload
```

#### 本地开发

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 代码格式化
make format

# 代码检查
make lint
```

### 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

## 繁體中文

### 🎉 專案介紹

WiFiDash 是一款智能WiFi網路診斷與視覺化工具，幫助使用者快速了解周圍的WiFi環境，優化網路配置，提升上網體驗。

**靈感來源**：在日常開發和辦公中，經常遇到WiFi訊號不穩定、頻道壅塞等問題。市面上雖然有一些WiFi分析工具，但要么功能複雜難用，要么需要付費。WiFiDash 旨在提供一個**簡潔、高效、開源**的替代方案。

**自研差異化亮點**：
- 🎨 美觀的TUI介面，無需瀏覽器即可使用
- 📊 即時頻道分析和壅塞檢測
- 💡 智慧優化建議（最佳頻道推薦、安全提醒）
- 🔧 支援CLI和TUI兩種使用模式
- 📤 一鍵匯出掃描結果

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📶 **網路掃描** | 掃描周圍所有WiFi網路，顯示SSID、訊號強度、加密方式等 |
| 📊 **頻道分析** | 分析2.4GHz和5GHz頻道使用情況，檢測壅塞 |
| 💡 **智慧建議** | 自動推薦最佳頻道，檢測安全漏洞 |
| 🖥️ **互動式TUI** | 基於Textual的美觀終端介面 |
| ⌨️ **CLI支援** | 支援命令列操作，方便腳本整合 |
| 📤 **資料匯出** | 支援JSON格式匯出，便於後續分析 |
| 🔒 **安全檢測** | 自動識別開放網路、WEP等不安全加密 |

### 🚀 快速開始

#### 環境要求

- Python 3.8+
- Linux/macOS/Windows
- 可選：WiFi網卡（用於真實掃描，否則使用演示資料）

#### 安裝

```bash
# 從PyPI安裝（推薦）
pip install wifidash

# 或從原始碼安裝
git clone https://github.com/gitstq/wifidash.git
cd wifidash
pip install -e .
```

#### 啟動TUI介面

```bash
wifidash
```

#### CLI命令

```bash
# 掃描WiFi網路
wifidash scan

# 以JSON格式輸出
wifidash scan --json

# 匯出到檔案
wifidash scan --export results.json

# 分析頻道
wifidash channels

# 取得最佳化建議
wifidash recommend

# 持續監控模式
wifidash monitor --interval 5
```

### 📖 詳細使用指南

#### TUI介面操作

| 快捷鍵 | 功能 |
|--------|------|
| `r` | 重新整理掃描 |
| `a` | 切換自動掃描 |
| `e` | 匯出資料 |
| `q` | 退出 |
| `?` | 顯示幫助 |

#### 訊號強度解讀

| 訊號強度 | 品質 | 說明 |
|----------|------|------|
| -30 ~ -50 dBm | 🟢 優秀 | 訊號很強，適合高畫質影片、遊戲 |
| -50 ~ -65 dBm | 🟡 良好 | 訊號良好，日常使用無壓力 |
| -65 ~ -75 dBm | 🟠 一般 | 訊號一般，可能有延遲 |
| -75 dBm以下 | 🔴 較差 | 訊號弱，建議調整位置 |

#### 頻道選擇建議

**2.4GHz頻段**：
- 推薦頻道：1、6、11（互不干擾）
- 避免使用：2-5、7-10（頻道重疊）

**5GHz頻段**：
- 推薦頻道：36、40、44、48、149、153、157、161
- 干擾較少，適合高速傳輸

### 💡 設計思路與迭代規劃

#### 技術選型原因

- **Python**：跨平台、生態豐富、易於維護
- **Textual**：現代化TUI框架，支援CSS樣式、動畫效果
- **Rich**：美觀的終端輸出，支援表格、進度條等

#### 後續功能迭代計劃

- [ ] 支援更多WiFi網卡驅動
- [ ] 新增歷史資料趨勢圖
- [ ] 支援WiFi 6E (6GHz) 分析
- [ ] 新增網路速度測試功能
- [ ] 支援匯出PDF報告

#### 社群貢獻方向

- 歡迎提交Issue和PR
- 支援更多語言的在地化
- 改進掃描演算法和準確性

### 📦 打包與部署指南

#### 構建安裝包

```bash
# 安裝構建依賴
pip install build twine

# 構建
make build

# 上傳到PyPI
make upload
```

#### 本地開發

```bash
# 安裝開發依賴
make install-dev

# 執行測試
make test

# 程式碼格式化
make format

# 程式碼檢查
make lint
```

### 🤝 貢獻指南

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 建立 Pull Request

### 📄 開源協議

本專案採用 [MIT](LICENSE) 協議開源。

---

## English

### 🎉 Project Introduction

WiFiDash is an intelligent WiFi network diagnostics and visualization tool that helps users quickly understand their surrounding WiFi environment, optimize network configuration, and improve their internet experience.

**Inspiration**: In daily development and office work, we often encounter WiFi signal instability and channel congestion issues. While there are some WiFi analysis tools on the market, they are either too complex to use or require payment. WiFiDash aims to provide a **simple, efficient, and open-source** alternative.

**Self-developed Differentiation Highlights**:
- 🎨 Beautiful TUI interface, no browser required
- 📊 Real-time channel analysis and congestion detection
- 💡 Intelligent optimization suggestions (best channel recommendations, security alerts)
- 🔧 Support for both CLI and TUI modes
- 📤 One-click export of scan results

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📶 **Network Scanning** | Scan all surrounding WiFi networks, display SSID, signal strength, encryption, etc. |
| 📊 **Channel Analysis** | Analyze 2.4GHz and 5GHz channel usage, detect congestion |
| 💡 **Smart Recommendations** | Automatically recommend best channels, detect security vulnerabilities |
| 🖥️ **Interactive TUI** | Beautiful terminal interface based on Textual |
| ⌨️ **CLI Support** | Command-line operations for easy script integration |
| 📤 **Data Export** | Export in JSON format for further analysis |
| 🔒 **Security Detection** | Automatically identify open networks, WEP, and other insecure encryption |

### 🚀 Quick Start

#### Requirements

- Python 3.8+
- Linux/macOS/Windows
- Optional: WiFi adapter (for real scanning, otherwise uses demo data)

#### Installation

```bash
# Install from PyPI (recommended)
pip install wifidash

# Or install from source
git clone https://github.com/gitstq/wifidash.git
cd wifidash
pip install -e .
```

#### Launch TUI

```bash
wifidash
```

#### CLI Commands

```bash
# Scan WiFi networks
wifidash scan

# Output in JSON format
wifidash scan --json

# Export to file
wifidash scan --export results.json

# Analyze channels
wifidash channels

# Get optimization recommendations
wifidash recommend

# Continuous monitoring mode
wifidash monitor --interval 5
```

### 📖 Detailed Usage Guide

#### TUI Interface Controls

| Shortcut | Function |
|----------|----------|
| `r` | Refresh scan |
| `a` | Toggle auto scan |
| `e` | Export data |
| `q` | Quit |
| `?` | Show help |

#### Signal Strength Interpretation

| Signal Strength | Quality | Description |
|-----------------|---------|-------------|
| -30 ~ -50 dBm | 🟢 Excellent | Strong signal, suitable for HD video and gaming |
| -50 ~ -65 dBm | 🟡 Good | Good signal, no pressure for daily use |
| -65 ~ -75 dBm | 🟠 Fair | Average signal, may have latency |
| Below -75 dBm | 🔴 Poor | Weak signal, recommend adjusting position |

#### Channel Selection Recommendations

**2.4GHz Band**:
- Recommended channels: 1, 6, 11 (non-overlapping)
- Avoid: 2-5, 7-10 (channel overlap)

**5GHz Band**:
- Recommended channels: 36, 40, 44, 48, 149, 153, 157, 161
- Less interference, suitable for high-speed transmission

### 💡 Design Philosophy and Iteration Planning

#### Technology Selection Rationale

- **Python**: Cross-platform, rich ecosystem, easy to maintain
- **Textual**: Modern TUI framework with CSS styling and animation support
- **Rich**: Beautiful terminal output with tables, progress bars, etc.

#### Future Feature Iteration Plans

- [ ] Support for more WiFi adapter drivers
- [ ] Add historical data trend charts
- [ ] Support WiFi 6E (6GHz) analysis
- [ ] Add network speed test functionality
- [ ] Support PDF report export

#### Community Contribution Directions

- Welcome Issues and PRs
- Support for more language localizations
- Improve scanning algorithms and accuracy

### 📦 Packaging and Deployment Guide

#### Build Package

```bash
# Install build dependencies
pip install build twine

# Build
make build

# Upload to PyPI
make upload
```

#### Local Development

```bash
# Install dev dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

### 🤝 Contributing Guidelines

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### 📄 License

This project is open-sourced under the [MIT](LICENSE) License.

---

<div align="center">

**Made with ❤️ by WiFiDash Team**

[Report Bug](https://github.com/gitstq/wifidash/issues) · [Request Feature](https://github.com/gitstq/wifidash/issues)

</div>
