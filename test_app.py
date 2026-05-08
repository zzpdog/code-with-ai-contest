"""
5G 信号可视化看板 - 单元测试

测试覆盖:
  1. 数据加载功能
  2. RSRP 颜色映射函数
  3. RSRP 信号等级判定函数
  4. 数据筛选逻辑
  5. 数据完整性校验

运行方式: pytest test_app.py -v
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app import load_data, rsrp_to_color, rsrp_to_color_hex, get_rsrp_level


# ============================================================
# 测试数据准备
# ============================================================

@pytest.fixture
def sample_csv(tmp_path):
    """创建临时测试 CSV 文件。"""
    csv_file = tmp_path / "test_signal.csv"
    data = {
        "Latitude": [31.21, 31.22, 31.23, 31.24, 31.25],
        "Longitude": [121.48, 121.49, 121.50, 121.51, 121.52],
        "CellID": [1001, 1002, 1003, 1004, 1005],
        "Band": ["n28", "n41", "n78", "n28", "n41"],
        "RSRP_dBm": [-75.0, -85.0, -95.0, -105.0, -115.0],
        "SINR_dB": [25.0, 15.0, 5.0, -5.0, -10.0],
        "TerminalType": ["Smartphone", "CPE", "IoT", "Smartphone", "CPE"],
        "Download_Mbps": [500.0, 600.0, 300.0, 200.0, 100.0],
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def sample_df():
    """创建测试用 DataFrame。"""
    return pd.DataFrame({
        "Latitude": [31.21, 31.22, 31.23],
        "Longitude": [121.48, 121.49, 121.50],
        "CellID": [1001, 1002, 1003],
        "Band": ["n28", "n41", "n78"],
        "RSRP_dBm": [-75.0, -95.0, -115.0],
        "SINR_dB": [25.0, 5.0, -10.0],
        "TerminalType": ["Smartphone", "CPE", "IoT"],
        "Download_Mbps": [500.0, 300.0, 100.0],
    })


# ============================================================
# 测试: 数据加载
# ============================================================

class TestDataLoading:
    """数据加载功能测试。"""

    def test_load_data_returns_dataframe(self, sample_csv):
        """验证 load_data 返回 DataFrame 类型。"""
        df = load_data(sample_csv)
        assert isinstance(df, pd.DataFrame)

    def test_load_data_correct_row_count(self, sample_csv):
        """验证加载的数据行数正确。"""
        df = load_data(sample_csv)
        assert len(df) == 5

    def test_load_data_correct_columns(self, sample_csv):
        """验证加载的数据包含所有必需列。"""
        df = load_data(sample_csv)
        expected_cols = [
            "Latitude", "Longitude", "CellID", "Band",
            "RSRP_dBm", "SINR_dB", "TerminalType", "Download_Mbps"
        ]
        for col in expected_cols:
            assert col in df.columns

    def test_load_data_numeric_types(self, sample_csv):
        """验证数值列被正确转换为数值类型。"""
        df = load_data(sample_csv)
        assert pd.api.types.is_numeric_dtype(df["RSRP_dBm"])
        assert pd.api.types.is_numeric_dtype(df["Download_Mbps"])

    def test_load_data_drops_na_coordinates(self, tmp_path):
        """验证缺失经纬度的行被正确过滤。"""
        csv_file = tmp_path / "test_na.csv"
        data = {
            "Latitude": [31.21, np.nan, 31.23],
            "Longitude": [121.48, 121.49, np.nan],
            "CellID": [1001, 1002, 1003],
            "Band": ["n28", "n41", "n78"],
            "RSRP_dBm": [-75.0, -85.0, -95.0],
            "SINR_dB": [25.0, 15.0, 5.0],
            "TerminalType": ["Smartphone", "CPE", "IoT"],
            "Download_Mbps": [500.0, 600.0, 300.0],
        }
        pd.DataFrame(data).to_csv(csv_file, index=False)
        df = load_data(str(csv_file))
        assert len(df) == 1  # 只有第一行有完整的经纬度


# ============================================================
# 测试: RSRP 颜色映射
# ============================================================

class TestRsrpToColor:
    """RSRP 颜色映射函数测试。"""

    def test_excellent_signal_green(self):
        """优秀信号 (> -80) 应返回绿色。"""
        assert rsrp_to_color(-75.0) == [0, 200, 0]

    def test_good_signal_light_green(self):
        """良好信号 (-80 ~ -90) 应返回浅绿色。"""
        assert rsrp_to_color(-85.0) == [100, 220, 50]

    def test_fair_signal_yellow(self):
        """一般信号 (-90 ~ -100) 应返回黄色。"""
        assert rsrp_to_color(-95.0) == [255, 200, 0]

    def test_poor_signal_orange(self):
        """较差信号 (-100 ~ -110) 应返回橙色。"""
        assert rsrp_to_color(-105.0) == [255, 120, 0]

    def test_bad_signal_red(self):
        """很差信号 (< -110) 应返回红色。"""
        assert rsrp_to_color(-115.0) == [255, 0, 0]

    def test_boundary_values(self):
        """测试边界值。"""
        # 恰好 -80: 应为浅绿 (>-80 为绿色, -80 不大于 -80)
        assert rsrp_to_color(-80.0) == [100, 220, 50]
        # 恰好 -90
        assert rsrp_to_color(-90.0) == [255, 200, 0]
        # 恰好 -100
        assert rsrp_to_color(-100.0) == [255, 120, 0]
        # 恰好 -110
        assert rsrp_to_color(-110.0) == [255, 0, 0]

    def test_returns_list_of_three(self):
        """验证返回值是长度为 3 的列表。"""
        color = rsrp_to_color(-90.0)
        assert isinstance(color, list)
        assert len(color) == 3
        assert all(isinstance(c, int) for c in color)


# ============================================================
# 测试: RSRP 十六进制颜色
# ============================================================

class TestRsrpToColorHex:
    """RSRP 十六进制颜色函数测试。"""

    def test_returns_hex_string(self):
        """验证返回十六进制颜色字符串。"""
        result = rsrp_to_color_hex(-90.0)
        assert isinstance(result, str)
        assert result.startswith("#")
        assert len(result) == 7

    def test_green_hex(self):
        """验证优秀信号十六进制颜色。"""
        assert rsrp_to_color_hex(-75.0) == "#00C800"

    def test_red_hex(self):
        """验证很差信号十六进制颜色。"""
        assert rsrp_to_color_hex(-115.0) == "#FF0000"


# ============================================================
# 测试: RSRP 信号等级
# ============================================================

class TestGetRsrpLevel:
    """RSRP 信号等级判定函数测试。"""

    def test_excellent(self):
        assert get_rsrp_level(-75.0) == "优秀"

    def test_good(self):
        assert get_rsrp_level(-85.0) == "良好"

    def test_fair(self):
        assert get_rsrp_level(-95.0) == "一般"

    def test_poor(self):
        assert get_rsrp_level(-105.0) == "较差"

    def test_bad(self):
        assert get_rsrp_level(-115.0) == "很差"

    def test_returns_string(self):
        """验证返回值为字符串。"""
        assert isinstance(get_rsrp_level(-90.0), str)


# ============================================================
# 测试: 数据完整性
# ============================================================

class TestDataIntegrity:
    """数据完整性校验测试。"""

    def test_band_values_valid(self, sample_df):
        """验证频段值在有效范围内。"""
        valid_bands = {"n28", "n41", "n78"}
        for band in sample_df["Band"]:
            assert band in valid_bands

    def test_rsrp_range_valid(self, sample_df):
        """验证 RSRP 值在合理物理范围内。"""
        for rsrp in sample_df["RSRP_dBm"]:
            assert -140 <= rsrp <= -44  # 5G RSRP 典型范围

    def test_download_speed_positive(self, sample_df):
        """验证下载速率为正数。"""
        for speed in sample_df["Download_Mbps"]:
            assert speed >= 0

    def test_latitude_range_shanghai(self, sample_df):
        """验证纬度在上海范围内。"""
        for lat in sample_df["Latitude"]:
            assert 30.7 <= lat <= 31.9  # 上海大致纬度范围

    def test_longitude_range_shanghai(self, sample_df):
        """验证经度在上海范围内。"""
        for lon in sample_df["Longitude"]:
            assert 120.8 <= lon <= 122.2  # 上海大致经度范围


# ============================================================
# 测试: 实际数据集加载
# ============================================================

class TestRealDataset:
    """使用实际数据集的集成测试。"""

    def test_real_data_loadable(self):
        """验证实际数据集可以正常加载。"""
        data_path = Path(__file__).parent / "data" / "signal_samples.csv"
        if data_path.exists():
            df = load_data(str(data_path))
            assert len(df) > 0
            assert "RSRP_dBm" in df.columns

    def test_real_data_has_all_bands(self):
        """验证实际数据集包含所有三种频段。"""
        data_path = Path(__file__).parent / "data" / "signal_samples.csv"
        if data_path.exists():
            df = load_data(str(data_path))
            bands = set(df["Band"].unique())
            assert bands.issuperset({"n28", "n41", "n78"})

    def test_real_data_has_all_terminal_types(self):
        """验证实际数据集包含所有三种终端类型。"""
        data_path = Path(__file__).parent / "data" / "signal_samples.csv"
        if data_path.exists():
            df = load_data(str(data_path))
            terminals = set(df["TerminalType"].unique())
            assert terminals.issuperset({"Smartphone", "CPE", "IoT"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
