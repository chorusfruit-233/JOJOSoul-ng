"""
Release reader module for reading and parsing RELEASE.md content
"""

import os
import re
import logging
from typing import Optional, Dict, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReleaseReader:
    """Class for reading and parsing release notes from RELEASE.md"""

    def __init__(self, release_file_path: str = "RELEASE.md"):
        """
        Initialize the ReleaseReader

        Args:
            release_file_path: Path to the RELEASE.md file
        """
        self.release_file_path = Path(release_file_path)
        self.content = ""
        self.versions = {}

    def read_release_file(self) -> bool:
        """
        Read the RELEASE.md file safely

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.release_file_path.exists():
                logger.error(
                    f"Release file not found: {self.release_file_path}"
                )
                return False

            with open(self.release_file_path, "r", encoding="utf-8") as f:
                self.content = f.read()

            logger.info(
                f"Successfully read release file: {self.release_file_path}"
            )
            return True

        except Exception as e:
            logger.error(f"Error reading release file: {e}")
            return False

    def parse_versions(self) -> Dict[str, Dict]:
        """
        Parse version information from the content

        Returns:
            Dict containing version data
        """
        if not self.content:
            logger.warning("No content to parse")
            return {}

        # Pattern to match version sections
        version_pattern = (
            r"### v([\d\.]+(?:-[\w]+)?) - (.+?) \((\d{4}-\d{2}-\d{2})\)"
        )

        # Find all version sections
        matches = list(
            re.finditer(version_pattern, self.content, re.MULTILINE)
        )

        for i, match in enumerate(matches):
            version = match.group(1)
            title = match.group(2)
            date = match.group(3)

            # Find the content for this version
            start_pos = match.start()
            end_pos = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(self.content)
            )

            version_content = self.content[start_pos:end_pos].strip()

            self.versions[version] = {
                "title": title,
                "date": date,
                "content": self._extract_version_content(version_content),
            }

        logger.info(f"Parsed {len(self.versions)} versions")
        return self.versions

    def _extract_version_content(self, version_content: str) -> str:
        """
        Extract raw content for a version from RELEASE.md

        Args:
            version_content: Raw version content

        Returns:
            Raw content string without version management section
        """
        # Find where version content ends (before next major section)
        lines = version_content.split("\n")
        filtered_lines = []

        for line in lines:
            if line.startswith("### v"):
                continue  # Skip version header
            if line.startswith("## 版本管理"):
                break  # Stop at version management section
            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def get_version_content(self, version: str) -> Optional[str]:
        """
        Get content for a specific version

        Args:
            version: Version string (e.g., "2.0.0")

        Returns:
            Raw content string or None if not found
        """
        if not self.versions:
            self.parse_versions()

        if version not in self.versions:
            logger.warning(f"Version {version} not found")
            return None

        version_data = self.versions[version]

        # Return the version header and content from RELEASE.md
        return f"### v{version} - {version_data['title']} ({version_data['date']})\n\n{version_data['content']}"

    def get_latest_version(self) -> Optional[str]:
        """
        Get the latest version number

        Returns:
            Latest version string or None if no versions found
        """
        if not self.versions:
            self.parse_versions()

        if not self.versions:
            return None

        # Sort versions by semantic version
        version_numbers = list(self.versions.keys())
        version_numbers.sort(
            key=lambda v: tuple(map(int, v.split("."))), reverse=True
        )

        return version_numbers[0] if version_numbers else None

    def generate_fallback_content(self, version: str) -> str:
        """
        Generate fallback content when file reading fails

        Args:
            version: Version string

        Returns:
            Fallback content string
        """
        return f"""## JOJO Soul v{version}

### 🎉 新增功能
- 基于 Python 的 JOJO 奇妙冒险同人游戏
- 完整的角色系统和战斗机制
- 五种元素属性战斗系统
- 商店系统和装备升级
- 多种难度选择
- 图形用户界面

### 📦 安装说明
1. 下载对应平台的可执行文件
2. 直接运行即可开始游戏

### 🌟 系统要求
- Windows 10/11
- macOS 10.14+
- Linux (支持图形界面)

查看完整更新日志请访问 [项目主页](https://github.com/chorusfruit-233/JOJOSoul-ng)
"""


def get_release_content(
    version: str, release_file_path: str = "RELEASE.md"
) -> str:
    """
    Convenience function to get release content for a version

    Args:
        version: Version string (e.g., "2.0.0")
        release_file_path: Path to RELEASE.md file

    Returns:
        Release content string
    """
    reader = ReleaseReader(release_file_path)

    if reader.read_release_file():
        content = reader.get_version_content(version)
        if content:
            return content

    # Fallback to generated content
    logger.warning(f"Using fallback content for version {version}")
    return reader.generate_fallback_content(version)


if __name__ == "__main__":
    # Test the module
    reader = ReleaseReader()
    if reader.read_release_file():
        versions = reader.parse_versions()
        latest = reader.get_latest_version()
        if latest:
            print(f"Latest version: {latest}")
            content = reader.get_version_content(latest)
            if content:
                print("Content preview:")
                print(content[:500] + "...")
    else:
        print("Failed to read release file")
