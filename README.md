# 📡 5G 信号可视化看板

> "Code with AI" 海选赛参赛项目 — 基于 Streamlit 的 5G 路测数据交互式可视化看板

## 🎯 项目简介

本项目利用 AI Coding Agent 辅助开发，使用纯 Python 框架 Streamlit 将 5G 路测模拟数据转化为一个功能丰富的交互式 Web 数据可视化看板。看板支持信号地图展示、数据图表分析、侧边栏联动筛选以及 3D 地图可视化等功能。

## ✨ 功能特性

### 🟢 基础关卡（已完成）

- **数据加载**: 使用 Pandas 读取 `signal_samples.csv`，支持数据预览与统计摘要
- **信号散点地图**: 基于 PyDeck 的交互式地图，数据点根据 RSRP 信号强度自动变色
  - 🟢 绿色: 优秀 (> -80 dBm)
  - 🟡 黄色: 一般 (-90 ~ -100 dBm)
  - 🔴 红色: 很差 (< -110 dBm)
- **数据概览图表**: 频段分布柱状图 + 终端类型饼图

### 🟡 进阶关卡（已完成）

- **侧边栏联动筛选**: 支持频段、终端类型、RSRP 范围、SINR 范围多维度筛选，地图与图表实时联动更新
- **3D 柱状地图**: 切换至 3D 视图，信号点以柱状图形式展示，柱高随下载速率变化
- **深度分析图表**: RSRP 分布直方图 + 各频段平均下载速率对比
- **工程化素养**: 完整的代码注释 + 单元测试覆盖

## 📁 项目结构

```
code-with-ai-contest/
├── data/
│   └── signal_samples.csv      # 5G 信号模拟数据集
├── app.py                      # Streamlit 主应用
├── test_app.py                 # 单元测试
├── requirements.txt            # Python 依赖
├── README.md                   # 项目说明（本文件）
└── AI_PROMPTS.md               # AI 交互日志
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，即可看到可视化看板。

### 3. 运行测试

```bash
pytest test_app.py -v
```

## 📊 数据集说明

| 字段 | 类型 | 说明 |
|------|------|------|
| Latitude | Float | 纬度（上海地区） |
| Longitude | Float | 经度（上海地区） |
| CellID | Integer | 小区 ID |
| Band | String | 5G 频段 (n28/n41/n78) |
| RSRP_dBm | Float | 参考信号接收功率 (dBm) |
| SINR_dB | Float | 信噪比 (dB) |
| TerminalType | String | 终端类型 (Smartphone/CPE/IoT) |
| Download_Mbps | Float | 下载速率 (Mbps) |

## 🛠️ 技术栈

- **Python 3.x** — 编程语言
- **Streamlit** — Web 应用框架
- **Pandas** — 数据处理
- **PyDeck** — 地图可视化（2D/3D）
- **Plotly** — 交互式图表
- **Pytest** — 单元测试

## 📸 功能截图说明

1. **2D 信号地图**: 散点根据 RSRP 信号强度变色，鼠标悬停可查看详细信息
2. **3D 柱状地图**: 柱高随下载速率变化，支持旋转和缩放
3. **侧边栏筛选**: 拖动滑块或选择频段/终端类型，地图和图表实时更新

## 📝 开发日志

本项目完全使用 AI Coding Agent 辅助开发，开发过程详见 `AI_PROMPTS.md`。

## 📄 许可证

本项目仅用于 "Code with AI" 海选赛参赛提交。
