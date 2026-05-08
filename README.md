# 📡 5G 信号可视化看板

> **"Code with AI" 海选赛参赛作品** — 将 5G 路测数据极速转化为交互式 Web 可视化看板

## 🌟 项目简介

本项目基于 Streamlit 框架，将 5G 路测模拟数据（`data/signal_samples.csv`）转化为一个功能丰富的交互式 Web 数据可视化看板。用户可以通过侧边栏筛选器实时过滤数据，地图和图表会联动更新。

## ✨ 功能特性

### 🟢 基础关卡功能

| 功能 | 说明 |
|------|------|
| **数据加载** | 使用 pandas 读取 CSV 数据，自动清洗和类型转换 |
| **信号散点地图** | 基于 pydeck 渲染交互式 2D 地图，数据点按 RSRP 信号强度变色（🟢 优秀 / 🟡 良好 / 🔴 较差） |
| **数据概览图表** | 各频段基站数量柱状图 + 终端类型占比饼图 |

### 🟡 进阶关卡功能

| 功能 | 说明 |
|------|------|
| **侧边栏联动筛选** | 频段下拉菜单、RSRP 范围滑动条、终端类型筛选、SINR 范围滑动条，拖动时地图和图表实时更新 |
| **3D 信号柱状地图** | 信号点以 3D 柱状图形式展示，柱体高度随下载速率(Download_Mbps)变化，颜色随 RSRP 变化 |
| **工程化素养** | 核心代码含规范注释和 docstring，附带完整单元测试 `test_app.py` |

### 📊 额外分析功能

- **信号质量深度分析**：RSRP 分布直方图 + 各频段 RSRP 箱线图
- **下载速率分析**：各频段平均下载速率柱状图 + 下载速率 vs RSRP 散点图
- **数据明细表格**：筛选后的数据明细展示
- **实时统计指标**：数据点总数、平均 RSRP、平均 SINR、平均下载速率等

## 🗂️ 项目结构

```
.
├── app.py                  # 主应用程序（Streamlit 看板）
├── test_app.py             # 单元测试
├── requirements.txt        # Python 依赖
├── README.md               # 项目说明文档
├── AI_PROMPTS.md           # AI Agent 交互日志
├── data/
│   └── signal_samples.csv  # 5G 路测模拟数据
└── screenshots/            # 运行截图
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.9+：

```bash
python --version
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

```bash
streamlit run app.py
```

启动后浏览器会自动打开 `http://localhost:8501`，即可看到 5G 信号可视化看板。

### 4. 运行测试

```bash
pytest test_app.py -v
```

## 📊 数据说明

数据文件 `data/signal_samples.csv` 包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| Latitude | float | 纬度（上海地区 ~31°N） |
| Longitude | float | 经度（上海地区 ~121°E） |
| CellID | int | 小区 ID |
| Band | str | 频段（n28 / n41 / n78） |
| RSRP_dBm | float | 信号强度（dBm），范围约 -120 ~ -70 |
| SINR_dB | float | 信噪比（dB） |
| TerminalType | str | 终端类型（Smartphone / CPE / IoT） |
| Download_Mbps | float | 下载速率（Mbps） |

### 信号质量判定标准

| RSRP 范围 | 信号质量 | 颜色 |
|-----------|---------|------|
| > -90 dBm | 优秀 | 🟢 绿色 |
| -110 ~ -90 dBm | 良好 | 🟡 黄色 |
| ≤ -110 dBm | 较差 | 🔴 红色 |

## 🛠️ 技术栈

- **[Streamlit](https://streamlit.io/)** — Web 应用框架
- **[Pydeck](https://deckgl.readthedocs.io/)** — 地理空间可视化（2D/3D 地图）
- **[Plotly](https://plotly.com/python/)** — 交互式图表
- **[Pandas](https://pandas.pydata.org/)** — 数据处理
- **[Pytest](https://pytest.org/)** — 单元测试

## 📸 运行截图

> 截图保存在 `screenshots/` 目录下，展示地图和侧边栏交互效果。

## 📄 提交物清单

- [x] 📂 源代码：`app.py` + `requirements.txt`（一键跑通）
- [x] 📄 项目说明文档：`README.md`
- [x] 📸 运行截图：`screenshots/` 目录
- [x] 🤖 Agent 交互日志：`AI_PROMPTS.md`

---

Built with ❤️ using AI Coding Agent | Streamlit + Pydeck + Plotly
