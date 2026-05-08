"""
5G 信号可视化看板 - "Code with AI" 海选赛项目

功能模块:
  1. 数据加载与预览
  2. 信号热力/散点地图（根据 RSRP 变色）
  3. 数据概览图表（频段统计 + 终端类型占比）
  4. 侧边栏联动筛选（频段、RSRP 范围、终端类型）
  5. 3D 地图可视化（柱状图高度随下载速率变化）

技术栈: Streamlit + Pandas + PyDeck + Plotly + NumPy
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# 工具函数
# ============================================================

def load_data(csv_path: str) -> pd.DataFrame:
    """
    加载 5G 信号 CSV 数据集。

    Args:
        csv_path: CSV 文件路径

    Returns:
        加载后的 DataFrame
    """
    df = pd.read_csv(csv_path)
    # 确保数值列类型正确
    numeric_cols = ["Latitude", "Longitude", "CellID", "RSRP_dBm",
                    "SINR_dB", "Download_Mbps"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Latitude", "Longitude"])


def rsrp_to_color(rsrp: float) -> list:
    """
    根据 RSRP 信号强度返回对应颜色 (RGB)。

    颜色分级:
      - 优秀 (> -80 dBm):  绿色 [0, 200, 0]
      - 良好 (-80 ~ -90):   浅绿 [100, 220, 50]
      - 一般 (-90 ~ -100):  黄色 [255, 200, 0]
      - 较差 (-100 ~ -110): 橙色 [255, 120, 0]
      - 很差 (< -110):      红色 [255, 0, 0]

    Args:
        rsrp: RSRP 信号强度值 (dBm)

    Returns:
        RGB 颜色列表 [R, G, B]
    """
    if rsrp > -80:
        return [0, 200, 0]
    elif rsrp > -90:
        return [100, 220, 50]
    elif rsrp > -100:
        return [255, 200, 0]
    elif rsrp > -110:
        return [255, 120, 0]
    else:
        return [255, 0, 0]


def rsrp_to_color_hex(rsrp: float) -> str:
    """
    根据 RSRP 值返回十六进制颜色字符串，用于 Plotly 图表。

    Args:
        rsrp: RSRP 信号强度值 (dBm)

    Returns:
        十六进制颜色字符串，如 "#00C800"
    """
    rgb = rsrp_to_color(rsrp)
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def get_rsrp_level(rsrp: float) -> str:
    """
    根据 RSRP 值返回信号等级描述。

    Args:
        rsrp: RSRP 信号强度值 (dBm)

    Returns:
        信号等级字符串
    """
    if rsrp > -80:
        return "优秀"
    elif rsrp > -90:
        return "良好"
    elif rsrp > -100:
        return "一般"
    elif rsrp > -110:
        return "较差"
    else:
        return "很差"


# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 10px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 数据加载（带缓存）
# ============================================================

@st.cache_data
def get_data():
    """缓存数据加载，避免重复读取文件。"""
    data_path = Path(__file__).parent / "data" / "signal_samples.csv"
    return load_data(str(data_path))


df = get_data()

# ============================================================
# 页面标题
# ============================================================

st.title("📡 5G 信号可视化看板")
st.markdown("---")
st.markdown(
    "欢迎来到 **'Code with AI' 极客探索赛**！"
    "本看板展示 5G 路测数据的交互式可视化分析结果。"
)

# ============================================================
# 侧边栏 - 联动筛选器（进阶关卡）
# ============================================================

with st.sidebar:
    st.header("🎛️ 数据筛选")

    # --- 频段筛选 ---
    all_bands = sorted(df["Band"].unique().tolist())
    selected_bands = st.multiselect(
        label="频段 Band",
        options=all_bands,
        default=all_bands,
        help="选择要展示的 5G 频段"
    )

    # --- 终端类型筛选 ---
    all_terminals = sorted(df["TerminalType"].unique().tolist())
    selected_terminals = st.multiselect(
        label="终端类型",
        options=all_terminals,
        default=all_terminals,
        help="选择要展示的终端类型"
    )

    # --- RSRP 范围滑动条 ---
    rsrp_min_val = float(df["RSRP_dBm"].min())
    rsrp_max_val = float(df["RSRP_dBm"].max())
    rsrp_range = st.slider(
        label="RSRP 范围 (dBm)",
        min_value=rsrp_min_val,
        max_value=rsrp_max_val,
        value=(rsrp_min_val, rsrp_max_val),
        step=1.0,
        help="拖动滑块筛选信号强度范围"
    )

    # --- SINR 范围滑动条 ---
    sinr_min_val = float(df["SINR_dB"].min())
    sinr_max_val = float(df["SINR_dB"].max())
    sinr_range = st.slider(
        label="SINR 范围 (dB)",
        min_value=sinr_min_val,
        max_value=sinr_max_val,
        value=(sinr_min_val, sinr_max_val),
        step=0.5,
        help="拖动滑块筛选信噪比范围"
    )

    st.markdown("---")

    # --- 地图视图切换 ---
    map_view = st.radio(
        label="地图视图",
        options=["2D 散点地图", "3D 柱状地图"],
        index=0,
        help="选择 2D 或 3D 地图展示模式"
    )

    st.markdown("---")
    st.caption("💡 调整筛选器后，右侧地图和图表将实时更新。")


# ============================================================
# 数据筛选
# ============================================================

filtered_df = df[
    (df["Band"].isin(selected_bands)) &
    (df["TerminalType"].isin(selected_terminals)) &
    (df["RSRP_dBm"] >= rsrp_range[0]) &
    (df["RSRP_dBm"] <= rsrp_range[1]) &
    (df["SINR_dB"] >= sinr_range[0]) &
    (df["SINR_dB"] <= sinr_range[1])
].copy()

# 为筛选后的数据添加颜色列
filtered_df["color"] = filtered_df["RSRP_dBm"].apply(rsrp_to_color)
filtered_df["color_hex"] = filtered_df["RSRP_dBm"].apply(rsrp_to_color_hex)
filtered_df["signal_level"] = filtered_df["RSRP_dBm"].apply(get_rsrp_level)


# ============================================================
# 顶部指标卡片
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 数据点总数",
        value=len(filtered_df),
        delta=f"筛选掉 {len(df) - len(filtered_df)} 条"
    )

with col2:
    avg_rsrp = filtered_df["RSRP_dBm"].mean() if len(filtered_df) > 0 else 0
    st.metric(
        label="📶 平均 RSRP",
        value=f"{avg_rsrp:.1f} dBm",
        delta=get_rsrp_level(avg_rsrp)
    )

with col3:
    avg_sinr = filtered_df["SINR_dB"].mean() if len(filtered_df) > 0 else 0
    st.metric(
        label="📡 平均 SINR",
        value=f"{avg_sinr:.1f} dB"
    )

with col4:
    avg_dl = filtered_df["Download_Mbps"].mean() if len(filtered_df) > 0 else 0
    st.metric(
        label="⬇️ 平均下载速率",
        value=f"{avg_dl:.1f} Mbps"
    )

st.markdown("---")


# ============================================================
# 信号地图可视化
# ============================================================

st.subheader("🗺️ 5G 信号地图")

if len(filtered_df) == 0:
    st.warning("⚠️ 当前筛选条件下没有数据，请调整筛选器。")
else:
    # 计算地图中心点
    center_lat = filtered_df["Latitude"].mean()
    center_lon = filtered_df["Longitude"].mean()

    if map_view == "2D 散点地图":
        # --- 2D 散点地图（基础关卡） ---
        # 使用 PyDeck ScatterplotLayer 实现根据 RSRP 变色
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=["Longitude", "Latitude"],
            get_color="color",
            get_radius=150,
            pickable=True,
            opacity=0.8,
            auto_highlight=True,
        )

        tooltip = {
            "html": """
            <div style="font-family: Arial; padding: 8px;">
                <b>小区ID:</b> {CellID}<br/>
                <b>频段:</b> {Band}<br/>
                <b>RSRP:</b> {RSRP_dBm} dBm<br/>
                <b>SINR:</b> {SINR_dB} dB<br/>
                <b>终端:</b> {TerminalType}<br/>
                <b>下载速率:</b> {Download_Mbps} Mbps
            </div>
            """,
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "borderRadius": "4px",
            }
        }

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            bearing=0
        )

        r = pdk.Deck(
            layers=[scatter_layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/light-v10",
            tooltip=tooltip
        )

        st.pydeck_chart(r)

    else:
        # --- 3D 柱状地图（进阶关卡 - 极客视觉体验） ---
        # 柱状图高度随下载速率变化
        filtered_df["elevation"] = filtered_df["Download_Mbps"] / 50.0  # 缩放因子

        column_layer = pdk.Layer(
            "ColumnLayer",
            data=filtered_df,
            get_position=["Longitude", "Latitude"],
            get_elevation="elevation",
            get_color="color",
            get_radius=80,
            pickable=True,
            opacity=0.85,
            auto_highlight=True,
            elevation_scale=10,
            coverage=0.9,
        )

        tooltip_3d = {
            "html": """
            <div style="font-family: Arial; padding: 8px;">
                <b>小区ID:</b> {CellID}<br/>
                <b>频段:</b> {Band}<br/>
                <b>RSRP:</b> {RSRP_dBm} dBm<br/>
                <b>下载速率:</b> {Download_Mbps} Mbps<br/>
                <b>柱高:</b> {elevation:.1f}
            </div>
            """,
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "borderRadius": "4px",
            }
        }

        view_state_3d = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=45,
            bearing=0
        )

        r_3d = pdk.Deck(
            layers=[column_layer],
            initial_view_state=view_state_3d,
            map_style="mapbox://styles/mapbox/light-v10",
            tooltip=tooltip_3d
        )

        st.pydeck_chart(r_3d)

    # RSRP 颜色图例
    st.markdown("**信号强度图例 (RSRP):**")
    legend_cols = st.columns(5)
    legend_items = [
        ("> -80 dBm", "#00C800", "优秀"),
        ("-80~-90 dBm", "#64DC32", "良好"),
        ("-90~-100 dBm", "#FFC800", "一般"),
        ("-100~-110 dBm", "#FF7800", "较差"),
        ("< -110 dBm", "#FF0000", "很差"),
    ]
    for i, (label, color, level) in enumerate(legend_items):
        with legend_cols[i]:
            st.markdown(
                f'<div style="text-align:center;">'
                f'<span style="display:inline-block;width:20px;height:20px;'
                f'background-color:{color};border-radius:3px;vertical-align:middle;"></span>'
                f'<br/><small>{label}<br/>({level})</small></div>',
                unsafe_allow_html=True
            )


st.markdown("---")


# ============================================================
# 数据概览图表（基础关卡）
# ============================================================

st.subheader("📊 数据概览图表")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # --- 柱状图: 各频段基站数量统计 ---
    st.markdown("**各频段数据点数量**")
    band_counts = filtered_df["Band"].value_counts().sort_index()

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=band_counts.index.tolist(),
        y=band_counts.values.tolist(),
        marker_color=["#4CAF50", "#2196F3", "#FF9800"],
        text=band_counts.values.tolist(),
        textposition="auto"
    ))
    fig_bar.update_layout(
        xaxis_title="频段 Band",
        yaxis_title="数据点数量",
        height=350,
        margin=dict(l=20, r=20, t=30, b=40),
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    # --- 饼图: 不同终端类型占比 ---
    st.markdown("**终端类型占比**")
    terminal_counts = filtered_df["TerminalType"].value_counts()

    fig_pie = go.Figure()
    fig_pie.add_trace(go.Pie(
        labels=terminal_counts.index.tolist(),
        values=terminal_counts.values.tolist(),
        hole=0.4,
        marker_colors=["#667eea", "#f093fb", "#4facfe"],
        textinfo="label+percent",
        textposition="outside"
    ))
    fig_pie.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=40),
        showlegend=True
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")


# ============================================================
# 进阶图表: RSRP 分布 + 下载速率分析
# ============================================================

st.subheader("📈 深度分析")

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    # --- RSRP 信号强度分布直方图 ---
    st.markdown("**RSRP 信号强度分布**")
    fig_hist = px.histogram(
        filtered_df,
        x="RSRP_dBm",
        nbins=20,
        color_discrete_sequence=["#667eea"],
        labels={"RSRP_dBm": "RSRP (dBm)", "count": "频次"},
    )
    # 添加信号等级分界线
    for threshold, label, color in [
        (-80, "优秀", "green"), (-90, "良好", "lightgreen"),
        (-100, "一般", "orange"), (-110, "较差", "red")
    ]:
        fig_hist.add_vline(
            x=threshold, line_dash="dash", line_color=color,
            annotation_text=label, annotation_position="top left"
        )
    fig_hist.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=40))
    st.plotly_chart(fig_hist, use_container_width=True)

with chart_col4:
    # --- 各频段平均下载速率对比 ---
    st.markdown("**各频段平均下载速率**")
    band_speed = filtered_df.groupby("Band")["Download_Mbps"].agg(
        ["mean", "max", "min"]
    ).reset_index()
    band_speed.columns = ["Band", "平均速率", "最大速率", "最小速率"]

    fig_speed = go.Figure()
    fig_speed.add_trace(go.Bar(
        x=band_speed["Band"],
        y=band_speed["平均速率"],
        name="平均速率",
        marker_color="#667eea",
        text=[f"{v:.1f}" for v in band_speed["平均速率"]],
        textposition="auto"
    ))
    fig_speed.add_trace(go.Bar(
        x=band_speed["Band"],
        y=band_speed["最大速率"],
        name="最大速率",
        marker_color="#4CAF50",
        text=[f"{v:.1f}" for v in band_speed["最大速率"]],
        textposition="auto"
    ))
    fig_speed.update_layout(
        barmode="group",
        xaxis_title="频段",
        yaxis_title="下载速率 (Mbps)",
        height=350,
        margin=dict(l=20, r=20, t=30, b=40),
        template="plotly_white"
    )
    st.plotly_chart(fig_speed, use_container_width=True)

st.markdown("---")


# ============================================================
# 数据预览表格
# ============================================================

st.subheader("📋 数据预览")

tab_preview, tab_stats = st.tabs(["数据表格", "统计摘要"])

with tab_preview:
    st.dataframe(
        filtered_df[["Latitude", "Longitude", "CellID", "Band",
                      "RSRP_dBm", "SINR_dB", "TerminalType",
                      "Download_Mbps", "signal_level"]],
        use_container_width=True,
        height=400,
        column_config={
            "signal_level": st.column_config.TextColumn("信号等级"),
        }
    )

with tab_stats:
    if len(filtered_df) > 0:
        stats_df = filtered_df[["RSRP_dBm", "SINR_dB", "Download_Mbps"]].describe()
        st.dataframe(stats_df, use_container_width=True)
    else:
        st.warning("无数据可统计。")


# ============================================================
# 页脚
# ============================================================

st.markdown("---")
st.caption(
    "📡 5G 信号可视化看板 | 'Code with AI' 海选赛项目 | "
    "Powered by Streamlit + PyDeck + Plotly"
)
