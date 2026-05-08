"""
5G 信号可视化看板 - "Code with AI" 海选赛参赛作品
====================================================
本应用使用 Streamlit 框架，将 5G 路测数据转化为交互式 Web 可视化看板。

功能模块：
    1. 数据加载：使用 pandas 读取 CSV 数据
    2. 信号散点地图：基于 pydeck 渲染交互地图，按 RSRP 信号强度变色
    3. 数据概览图表：各频段基站数量柱状图 & 终端类型占比饼图
    4. 侧边栏联动筛选：频段下拉菜单、RSRP 范围滑动条、终端类型筛选
    5. 3D 地图：信号点以 3D 柱状图形式展示，高度随下载速率变化
    6. 数据统计摘要：关键指标的实时统计

作者：Code with AI 参赛团队
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# 数据加载模块
# ============================================================

@st.cache_data
def load_data(filepath: str = "data/signal_samples.csv") -> pd.DataFrame:
    """
    使用 pandas 读取 CSV 数据文件。

    Args:
        filepath: CSV 文件路径，默认为 data/signal_samples.csv

    Returns:
        pd.DataFrame: 包含 5G 信号数据的 DataFrame

    Raises:
        FileNotFoundError: 当数据文件不存在时抛出
    """
    data_path = Path(filepath)
    if not data_path.exists():
        st.error(f"❌ 数据文件未找到：{filepath}，请确认文件路径是否正确。")
        st.stop()

    df = pd.read_csv(filepath)

    # 数据清洗：去除空值行
    df = df.dropna()

    # 确保数值列类型正确
    numeric_cols = ["Latitude", "Longitude", "RSRP_dBm", "SINR_dB", "Download_Mbps"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=numeric_cols)

    return df


def classify_signal_strength(rsrp: float) -> str:
    """
    根据 RSRP 信号强度分类信号质量等级。

    Args:
        rsrp: 信号强度值（dBm）

    Returns:
        str: 信号质量等级描述
            - "优秀" : RSRP > -90 dBm
            - "良好" : -110 dBm < RSRP <= -90 dBm
            - "较差" : RSRP <= -110 dBm
    """
    if rsrp > -90:
        return "优秀"
    elif rsrp > -110:
        return "良好"
    else:
        return "较差"


def get_signal_color(rsrp: float) -> list:
    """
    根据 RSRP 信号强度返回对应的 RGBA 颜色值。

    颜色映射规则：
        - RSRP > -90 dBm  → 绿色 [0, 200, 0, 200]
        - -110 < RSRP <= -90 dBm → 黄色 [255, 200, 0, 200]
        - RSRP <= -110 dBm → 红色 [255, 0, 0, 200]

    Args:
        rsrp: 信号强度值（dBm）

    Returns:
        list: RGBA 颜色值列表 [R, G, B, A]
    """
    if rsrp > -90:
        return [0, 200, 0, 200]      # 绿色 - 信号优秀
    elif rsrp > -110:
        return [255, 200, 0, 200]    # 黄色 - 信号良好
    else:
        return [255, 0, 0, 200]      # 红色 - 信号较差


# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载数据
df = load_data()

# 为数据添加辅助列
df["信号质量"] = df["RSRP_dBm"].apply(classify_signal_strength)
df["颜色"] = df["RSRP_dBm"].apply(get_signal_color)

# ============================================================
# 侧边栏 - 联动筛选器（进阶关卡）
# ============================================================

st.sidebar.header("🔧 数据筛选器")
st.sidebar.markdown("---")

# 频段筛选器
bands = sorted(df["Band"].unique())
selected_bands = st.sidebar.multiselect(
    "📶 选择频段 (Band)",
    options=bands,
    default=bands,
    help="选择一个或多个频段进行筛选，地图和图表将实时更新"
)

# RSRP 范围滑动条
rsrp_min = int(df["RSRP_dBm"].min())
rsrp_max = int(df["RSRP_dBm"].max())
rsrp_range = st.sidebar.slider(
    "📊 RSRP 信号强度范围 (dBm)",
    min_value=rsrp_min,
    max_value=rsrp_max,
    value=(rsrp_min, rsrp_max),
    step=1,
    help="拖动滑块筛选指定 RSRP 范围内的数据点"
)

# 终端类型筛选器
terminal_types = sorted(df["TerminalType"].unique())
selected_terminals = st.sidebar.multiselect(
    "📱 选择终端类型",
    options=terminal_types,
    default=terminal_types,
    help="选择一个或多个终端类型进行筛选"
)

# SINR 范围滑动条
sinr_min = float(df["SINR_dB"].min())
sinr_max = float(df["SINR_dB"].max())
sinr_range = st.sidebar.slider(
    "📶 SINR 信噪比范围 (dB)",
    min_value=sinr_min,
    max_value=sinr_max,
    value=(sinr_min, sinr_max),
    step=0.5,
    help="拖动滑块筛选指定 SINR 范围内的数据点"
)

st.sidebar.markdown("---")

# 应用筛选条件
filtered_df = df[
    (df["Band"].isin(selected_bands))
    & (df["RSRP_dBm"] >= rsrp_range[0])
    & (df["RSRP_dBm"] <= rsrp_range[1])
    & (df["TerminalType"].isin(selected_terminals))
    & (df["SINR_dB"] >= sinr_range[0])
    & (df["SINR_dB"] <= sinr_range[1])
].copy()

# 重新计算筛选后数据的颜色
filtered_df["颜色"] = filtered_df["RSRP_dBm"].apply(get_signal_color)

# 侧边栏统计信息
st.sidebar.markdown("### 📋 筛选结果统计")
st.sidebar.metric("数据点数量", f"{len(filtered_df)} / {len(df)}")
if len(filtered_df) > 0:
    st.sidebar.metric("平均 RSRP", f"{filtered_df['RSRP_dBm'].mean():.2f} dBm")
    st.sidebar.metric("平均 SINR", f"{filtered_df['SINR_dB'].mean():.2f} dB")
    st.sidebar.metric("平均下载速率", f"{filtered_df['Download_Mbps'].mean():.2f} Mbps")

# ============================================================
# 主页面内容
# ============================================================

st.title("📡 5G 信号可视化看板")
st.markdown("##### 🚀 Powered by AI Coding Agent | Streamlit + Pydeck + Plotly")
st.markdown("---")

# 数据概览指标卡片
if len(filtered_df) > 0:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📍 数据点总数", f"{len(filtered_df)}")
    with col2:
        st.metric("📶 平均 RSRP", f"{filtered_df['RSRP_dBm'].mean():.1f} dBm")
    with col3:
        st.metric("📊 平均 SINR", f"{filtered_df['SINR_dB'].mean():.1f} dB")
    with col4:
        st.metric("⬇️ 平均下载速率", f"{filtered_df['Download_Mbps'].mean():.1f} Mbps")
    with col5:
        st.metric("📶 频段数", f"{filtered_df['Band'].nunique()}")
else:
    st.warning("⚠️ 当前筛选条件下没有数据，请调整筛选器。")

st.markdown("---")

# ============================================================
# 2D 信号散点地图（基础关卡）
# ============================================================

st.subheader("🗺️ 信号覆盖地图 - 2D 视图")
st.caption("地图上的点根据 RSRP 信号强度变色：🟢 优秀(>-90dBm) | 🟡 良好(-110~-90dBm) | 🔴 较差(≤-110dBm)")

if len(filtered_df) > 0:
    # 使用 pydeck 渲染交互式散点地图
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_color="颜色",
        get_radius=80,
        radius_min_pixels=5,
        radius_max_pixels=15,
        pickable=True,
        opacity=0.8,
    )

    # 计算地图中心点
    center_lon = filtered_df["Longitude"].mean()
    center_lat = filtered_df["Latitude"].mean()

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=0,
    )

    scatter_deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=view_state,
        layers=[scatter_layer],
        tooltip={
            "html": """
                <b>小区ID:</b> {CellID}<br/>
                <b>频段:</b> {Band}<br/>
                <b>RSRP:</b> {RSRP_dBm} dBm<br/>
                <b>SINR:</b> {SINR_dB} dB<br/>
                <b>终端:</b> {TerminalType}<br/>
                <b>下载速率:</b> {Download_Mbps} Mbps
            """,
            "style": {
                "backgroundColor": "rgba(0, 0, 0, 0.8)",
                "color": "white",
                "fontFamily": "monospace",
                "fontSize": "12px",
            }
        }
    )

    st.pydeck_chart(scatter_deck, use_container_width=True)
else:
    st.info("请调整筛选条件以显示地图数据。")

st.markdown("---")

# ============================================================
# 3D 信号地图（进阶关卡 - 极客视觉体验）
# ============================================================

st.subheader("🏙️ 3D 信号柱状地图 - 极客视觉")
st.caption("信号点以 3D 柱状图形式展示，柱体高度随下载速率(Download_Mbps)变化，颜色随 RSRP 信号强度变化")

if len(filtered_df) > 0:
    # 3D 柱状图层 - 高度随下载速率变化
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Download_Mbps",
        elevation_scale=0.5,
        radius=60,
        get_fill_color="颜色",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # 3D 视角
    view_state_3d = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=45,
        bearing=20,
    )

    deck_3d = pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state_3d,
        layers=[column_layer],
        tooltip={
            "html": """
                <b>小区ID:</b> {CellID}<br/>
                <b>频段:</b> {Band}<br/>
                <b>RSRP:</b> {RSRP_dBm} dBm<br/>
                <b>SINR:</b> {SINR_dB} dB<br/>
                <b>终端:</b> {TerminalType}<br/>
                <b>下载速率:</b> {Download_Mbps} Mbps<br/>
                <b>信号质量:</b> {信号质量}
            """,
            "style": {
                "backgroundColor": "rgba(0, 0, 0, 0.85)",
                "color": "white",
                "fontFamily": "monospace",
                "fontSize": "12px",
            }
        }
    )

    st.pydeck_chart(deck_3d, use_container_width=True)
else:
    st.info("请调整筛选条件以显示 3D 地图数据。")

st.markdown("---")

# ============================================================
# 数据概览图表（基础关卡）
# ============================================================

st.subheader("📊 数据概览图表")

if len(filtered_df) > 0:
    chart_col1, chart_col2 = st.columns(2)

    # 图表1：各频段基站数量柱状图
    with chart_col1:
        st.markdown("#### 📶 各频段基站数量")
        band_counts = filtered_df.groupby("Band").size().reset_index(name="基站数量")
        band_counts = band_counts.sort_values("基站数量", ascending=False)

        fig_bar = px.bar(
            band_counts,
            x="Band",
            y="基站数量",
            color="Band",
            color_discrete_sequence=px.colors.qualitative.Set2,
            text="基站数量",
            title="各频段 (Band) 基站数量统计",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            xaxis_title="频段 (Band)",
            yaxis_title="基站数量",
            showlegend=False,
            height=400,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # 图表2：终端类型占比饼图
    with chart_col2:
        st.markdown("#### 📱 终端类型占比")
        terminal_counts = filtered_df.groupby("TerminalType").size().reset_index(name="数量")

        fig_pie = px.pie(
            terminal_counts,
            names="TerminalType",
            values="数量",
            color="TerminalType",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="不同类型终端占比",
            hole=0.4,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont_size=14,
        )
        fig_pie.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # 信号质量分布图表
    # ============================================================

    st.subheader("📈 信号质量深度分析")

    analysis_col1, analysis_col2 = st.columns(2)

    with analysis_col1:
        # RSRP 信号强度分布直方图
        st.markdown("#### RSRP 信号强度分布")
        fig_rsrp = px.histogram(
            filtered_df,
            x="RSRP_dBm",
            nbins=30,
            color="信号质量",
            color_discrete_map={
                "优秀": "#00C800",
                "良好": "#FFC800",
                "较差": "#FF0000",
            },
            title="RSRP 信号强度分布直方图",
            labels={"RSRP_dBm": "RSRP (dBm)", "count": "数据点数量"},
        )
        fig_rsrp.update_layout(height=400, bargap=0.05)
        # 添加阈值线
        fig_rsrp.add_vline(x=-90, line_dash="dash", line_color="green", annotation_text="-90 dBm")
        fig_rsrp.add_vline(x=-110, line_dash="dash", line_color="red", annotation_text="-110 dBm")
        st.plotly_chart(fig_rsrp, use_container_width=True)

    with analysis_col2:
        # 各频段 RSRP 箱线图
        st.markdown("#### 各频段 RSRP 分布")
        fig_box = px.box(
            filtered_df,
            x="Band",
            y="RSRP_dBm",
            color="Band",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="各频段 RSRP 信号强度箱线图",
            labels={"RSRP_dBm": "RSRP (dBm)", "Band": "频段"},
        )
        fig_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # 下载速率分析
    # ============================================================

    st.subheader("⬇️ 下载速率分析")

    speed_col1, speed_col2 = st.columns(2)

    with speed_col1:
        # 各频段平均下载速率
        st.markdown("#### 各频段平均下载速率")
        avg_speed = filtered_df.groupby("Band")["Download_Mbps"].mean().reset_index()
        avg_speed = avg_speed.sort_values("Download_Mbps", ascending=False)

        fig_speed = px.bar(
            avg_speed,
            x="Band",
            y="Download_Mbps",
            color="Band",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            text="Download_Mbps",
            title="各频段平均下载速率 (Mbps)",
        )
        fig_speed.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_speed.update_layout(
            xaxis_title="频段 (Band)",
            yaxis_title="平均下载速率 (Mbps)",
            showlegend=False,
            height=400,
        )
        st.plotly_chart(fig_speed, use_container_width=True)

    with speed_col2:
        # 下载速率 vs RSRP 散点图
        st.markdown("#### 下载速率 vs RSRP 关系")
        # SINR 可能为负值，需要偏移为正值才能用作气泡大小
        scatter_df = filtered_df.copy()
        scatter_df["SINR_size"] = scatter_df["SINR_dB"] - scatter_df["SINR_dB"].min() + 1

        fig_scatter = px.scatter(
            scatter_df,
            x="RSRP_dBm",
            y="Download_Mbps",
            color="Band",
            size="SINR_size",
            hover_data=["CellID", "TerminalType", "SINR_dB"],
            title="下载速率与 RSRP 信号强度关系",
            labels={"RSRP_dBm": "RSRP (dBm)", "Download_Mbps": "下载速率 (Mbps)"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # 数据表格展示
    # ============================================================

    st.subheader("📋 筛选后数据明细")
    st.caption(f"当前显示 {len(filtered_df)} 条数据记录")

    # 显示关键列
    display_cols = ["Latitude", "Longitude", "CellID", "Band", "RSRP_dBm", "SINR_dB", "TerminalType", "Download_Mbps", "信号质量"]
    st.dataframe(
        filtered_df[display_cols].sort_values("RSRP_dBm", ascending=False),
        use_container_width=True,
        height=300,
    )

else:
    st.warning("⚠️ 当前筛选条件下没有数据，请调整侧边栏筛选器。")

# ============================================================
# 页脚
# ============================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 12px;'>
        📡 5G 信号可视化看板 | "Code with AI" 海选赛参赛作品<br/>
        Built with ❤️ using Streamlit + Pydeck + Plotly | Powered by AI Coding Agent
    </div>
    """,
    unsafe_allow_html=True,
)
