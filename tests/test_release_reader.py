"""
Tests for release_reader module
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.release_reader import ReleaseReader, get_release_content


class TestReleaseReader:
    """Test cases for ReleaseReader class"""

    def test_init(self):
        """Test ReleaseReader initialization"""
        reader = ReleaseReader()
        assert reader.release_file_path == Path("RELEASE.md")
        assert reader.content == ""
        assert reader.versions == {}

        reader = ReleaseReader("custom.md")
        assert reader.release_file_path == Path("custom.md")

    def test_read_release_file_success(self):
        """Test successful file reading"""
        # Create a temporary release file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as f:
            f.write(
                """# 发布指南

## 最新发布

### v2.0.0 - 内容扩展版 (2025-12-14)

#### 🎉 新增功能
- 新增4个地图区域
"""
            )
            temp_file = f.name

        try:
            reader = ReleaseReader(temp_file)
            assert reader.read_release_file() is True
            assert "内容扩展版" in reader.content
        finally:
            os.unlink(temp_file)

    def test_read_release_file_not_found(self):
        """Test file not found error"""
        reader = ReleaseReader("nonexistent.md")
        assert reader.read_release_file() is False

    def test_parse_versions(self):
        """Test version parsing"""
        # Create a temporary release file with multiple versions
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as f:
            f.write(
                """# 发布指南

## 最新发布

### v2.0.0 - 内容扩展版 (2025-12-14)
#### 🎉 新增功能
- 新增4个地图区域

### v1.0.0 - 重构版 (2025-01-01)
#### 🎉 新增功能
- 基础游戏功能
"""
            )
            temp_file = f.name

        try:
            reader = ReleaseReader(temp_file)
            reader.read_release_file()
            versions = reader.parse_versions()

            assert "2.0.0" in versions
            assert "1.0.0" in versions
            assert versions["2.0.0"]["title"] == "内容扩展版"
            assert versions["2.0.0"]["date"] == "2025-12-14"
            assert versions["1.0.0"]["title"] == "重构版"
            assert versions["1.0.0"]["date"] == "2025-01-01"
        finally:
            os.unlink(temp_file)

    def test_parse_versions_empty_content(self):
        """Test parsing with empty content"""
        reader = ReleaseReader()
        versions = reader.parse_versions()
        assert versions == {}

    def test_get_version_content(self):
        """Test getting version content"""
        # Create a temporary release file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as f:
            f.write(
                """# 发布指南

## 最新发布

### v2.0.0 - 内容扩展版 (2025-12-14)
#### 🎉 新增功能
- 新增4个地图区域
- 新增3种敌人类型
"""
            )
            temp_file = f.name

        try:
            reader = ReleaseReader(temp_file)
            reader.read_release_file()

            content = reader.get_version_content("2.0.0")
            assert content is not None
            assert "JOJO Soul v2.0.0" in content
            assert "内容扩展版" in content
            assert "新增4个地图区域" in content
            assert "安装说明" in content
        finally:
            os.unlink(temp_file)

    def test_get_version_content_not_found(self):
        """Test getting content for non-existent version"""
        reader = ReleaseReader()
        content = reader.get_version_content("9.9.9")
        assert content is None

    def test_get_latest_version(self):
        """Test getting latest version"""
        # Create a temporary release file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as f:
            f.write(
                """# 发布指南

### v1.5.0 - 中间版本 (2025-06-01)
#### 🎉 新增功能
- 中间功能

### v2.0.0 - 内容扩展版 (2025-12-14)
#### 🎉 新增功能
- 新增功能

### v1.0.0 - 重构版 (2025-01-01)
#### 🎉 新增功能
- 基础功能
"""
            )
            temp_file = f.name

        try:
            reader = ReleaseReader(temp_file)
            reader.read_release_file()

            latest = reader.get_latest_version()
            assert latest == "2.0.0"
        finally:
            os.unlink(temp_file)

    def test_get_latest_version_no_versions(self):
        """Test getting latest version with no versions parsed"""
        reader = ReleaseReader()
        latest = reader.get_latest_version()
        assert latest is None

    def test_generate_fallback_content(self):
        """Test fallback content generation"""
        reader = ReleaseReader()
        content = reader.generate_fallback_content("2.0.0")

        assert "JOJO Soul v2.0.0" in content
        assert "基于 Python 的 JOJO 奇妙冒险同人游戏" in content
        assert "安装说明" in content
        assert "系统要求" in content


class TestGetReleaseContent:
    """Test cases for get_release_content function"""

    def test_get_release_content_success(self):
        """Test successful content retrieval"""
        # Create a temporary release file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".md"
        ) as f:
            f.write(
                """# 发布指南

### v2.0.0 - 内容扩展版 (2025-12-14)
#### 🎉 新增功能
- 新增4个地图区域
"""
            )
            temp_file = f.name

        try:
            content = get_release_content("2.0.0", temp_file)
            assert content is not None
            assert "JOJO Soul v2.0.0" in content
            assert "内容扩展版" in content
        finally:
            os.unlink(temp_file)

    def test_get_release_content_fallback(self):
        """Test fallback when file doesn't exist"""
        content = get_release_content("2.0.0", "nonexistent.md")
        assert content is not None
        assert "JOJO Soul v2.0.0" in content
        assert "基于 Python 的 JOJO 奇妙冒险同人游戏" in content


if __name__ == "__main__":
    pytest.main([__file__])
