"""
5G 信号可视化看板 - 单元测试模块
====================================
对 app.py 中的核心函数进行单元测试，确保数据加载、信号分类和颜色映射逻辑正确。

运行方式：
    pytest test_app.py -v
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app import classify_signal_strength, get_signal_color


# ============================================================
# classify_signal_strength 函数测试
# ============================================================

class TestClassifySignalStrength:
    """测试 classify_signal_strength 信号质量分类函数。"""

    def test_excellent_signal(self):
        """RSRP > -90 dBm 应分类为'优秀'。"""
        assert classify_signal_strength(-80) == "优秀"
        assert classify_signal_strength(-89) == "优秀"
        assert classify_signal_strength(-70) == "优秀"
        assert classify_signal_strength(-50) == "优秀"

    def test_good_signal(self):
        """-110 < RSRP <= -90 dBm 应分类为'良好'。"""
        assert classify_signal_strength(-90) == "良好"
        assert classify_signal_strength(-100) == "良好"
        assert classify_signal_strength(-109) == "良好"
        assert classify_signal_strength(-95) == "良好"

    def test_poor_signal(self):
        """RSRP <= -110 dBm 应分类为'较差'。"""
        assert classify_signal_strength(-110) == "较差"
        assert classify_signal_strength(-120) == "较差"
        assert classify_signal_strength(-130) == "较差"

    def test_boundary_values(self):
        """测试边界值。"""
        # -90 dBm 是优秀和良好的分界线，应归为良好
        assert classify_signal_strength(-90) == "良好"
        # -110 dBm 是良好和较差的分界线，应归为较差
        assert classify_signal_strength(-110) == "较差"
        # -89.99 应归为优秀
        assert classify_signal_strength(-89.99) == "优秀"
        # -109.99 应归为良好
        assert classify_signal_strength(-109.99) == "良好"


# ============================================================
# get_signal_color 函数测试
# ============================================================

class TestGetSignalColor:
    """测试 get_signal_color 颜色映射函数。"""

    def test_excellent_color(self):
        """RSRP > -90 dBm 应返回绿色。"""
        color = get_signal_color(-80)
        assert color == [0, 200, 0, 200]

    def test_good_color(self):
        """-110 < RSRP <= -90 dBm 应返回黄色。"""
        color = get_signal_color(-100)
        assert color == [255, 200, 0, 200]

    def test_poor_color(self):
        """RSRP <= -110 dBm 应返回红色。"""
        color = get_signal_color(-120)
        assert color == [255, 0, 0, 200]

    def test_color_format(self):
        """颜色值应为包含4个整数的列表 [R, G, B, A]。"""
        for rsrp in [-80, -100, -120]:
            color = get_signal_color(rsrp)
            assert isinstance(color, list)
            assert len(color) == 4
            for c in color:
                assert isinstance(c, int)
                assert 0 <= c <= 255

    def test_boundary_colors(self):
        """测试边界值的颜色映射。"""
        # -90 dBm 边界
        assert get_signal_color(-90) == [255, 200, 0, 200]  # 黄色
        # -110 dBm 边界
        assert get_signal_color(-110) == [255, 0, 0, 200]   # 红色


# ============================================================
# 数据文件完整性测试
# ============================================================

class TestDataIntegrity:
    """测试数据文件的完整性和格式。"""

    @pytest.fixture
    def sample_df(self):
        """加载测试数据集。"""
        data_path = Path(__file__).parent / "data" / "signal_samples.csv"
        if not data_path.exists():
            pytest.skip("数据文件不存在，跳过数据完整性测试")
        return pd.read_csv(data_path)

    def test_data_file_exists(self):
        """验证数据文件存在。"""
        data_path = Path(__file__).parent / "data" / "signal_samples.csv"
        assert data_path.exists(), "数据文件 data/signal_samples.csv 不存在"

    def test_required_columns(self, sample_df):
        """验证数据集包含所有必需列。"""
        required_cols = ["Latitude", "Longitude", "CellID", "Band", "RSRP_dBm", "SINR_dB", "TerminalType", "Download_Mbps"]
        for col in required_cols:
            assert col in sample_df.columns, f"缺少必需列：{col}"

    def test_data_not_empty(self, sample_df):
        """验证数据集不为空。"""
        assert len(sample_df) > 0, "数据集为空"

    def test_latitude_range(self, sample_df):
        """验证纬度值在合理范围内（上海地区约 31°N）。"""
        valid_lat = sample_df["Latitude"].dropna()
        assert valid_lat.min() >= 30, f"纬度最小值 {valid_lat.min()} 不在合理范围"
        assert valid_lat.max() <= 32, f"纬度最大值 {valid_lat.max()} 不在合理范围"

    def test_longitude_range(self, sample_df):
        """验证经度值在合理范围内（上海地区约 121°E）。"""
        valid_lon = sample_df["Longitude"].dropna()
        assert valid_lon.min() >= 120, f"经度最小值 {valid_lon.min()} 不在合理范围"
        assert valid_lon.max() <= 122, f"经度最大值 {valid_lon.max()} 不在合理范围"

    def test_rsrp_range(self, sample_df):
        """验证 RSRP 值在合理范围内（5G 信号通常 -140 ~ -44 dBm）。"""
        valid_rsrp = sample_df["RSRP_dBm"].dropna()
        assert valid_rsrp.min() >= -140, f"RSRP 最小值 {valid_rsrp.min()} 不在合理范围"
        assert valid_rsrp.max() <= -44, f"RSRP 最大值 {valid_rsrp.max()} 不在合理范围"

    def test_band_values(self, sample_df):
        """验证频段值为已知的 5G 频段。"""
        valid_bands = {"n28", "n41", "n78", "n79", "n1", "n3", "n77"}
        actual_bands = set(sample_df["Band"].dropna().unique())
        # 允许数据中包含的频段是已知频段的子集
        assert actual_bands.issubset(valid_bands), f"发现未知频段：{actual_bands - valid_bands}"

    def test_terminal_type_values(self, sample_df):
        """验证终端类型为已知类型。"""
        valid_types = {"Smartphone", "CPE", "IoT"}
        actual_types = set(sample_df["TerminalType"].dropna().unique())
        assert actual_types.issubset(valid_types), f"发现未知终端类型：{actual_types - valid_types}"

    def test_download_speed_positive(self, sample_df):
        """验证下载速率为正值。"""
        valid_speed = sample_df["Download_Mbps"].dropna()
        assert (valid_speed > 0).all(), "下载速率存在非正值"


# ============================================================
# 数据处理逻辑测试
# ============================================================

class TestDataProcessing:
    """测试数据处理相关逻辑。"""

    def test_signal_classification_consistency(self):
        """验证信号分类与颜色映射的一致性。"""
        test_rsrp_values = [-70, -80, -90, -95, -100, -110, -120]
        for rsrp in test_rsrp_values:
            quality = classify_signal_strength(rsrp)
            color = get_signal_color(rsrp)
            if quality == "优秀":
                assert color[1] == 200 and color[0] == 0  # 绿色
            elif quality == "良好":
                assert color[0] == 255 and color[1] == 200  # 黄色
            elif quality == "较差":
                assert color[0] == 255 and color[1] == 0  # 红色

    def test_filter_logic(self):
        """测试筛选逻辑是否正确。"""
        # 创建测试数据
        test_data = pd.DataFrame({
            "Band": ["n28", "n78", "n41", "n28", "n78"],
            "RSRP_dBm": [-80, -100, -115, -85, -95],
            "TerminalType": ["Smartphone", "CPE", "IoT", "Smartphone", "CPE"],
            "SINR_dB": [10, 15, -2, 20, 5],
        })

        # 测试频段筛选
        filtered = test_data[test_data["Band"].isin(["n28"])]
        assert len(filtered) == 2
        assert set(filtered["Band"]) == {"n28"}

        # 测试 RSRP 范围筛选（-100 到 -80 包含 -80, -100, -85, -95 共4个值）
        filtered = test_data[(test_data["RSRP_dBm"] >= -100) & (test_data["RSRP_dBm"] <= -80)]
        assert len(filtered) == 4

        # 测试终端类型筛选
        filtered = test_data[test_data["TerminalType"].isin(["CPE"])]
        assert len(filtered) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
