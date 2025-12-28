#!/usr/bin/env python3
"""
Release content generator script for JOJO Soul game
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.release_reader import get_release_content


def main():
    """Main function to generate release content"""
    parser = argparse.ArgumentParser(
        description="Generate release content from RELEASE.md"
    )
    parser.add_argument(
        "--version",
        "-v",
        required=True,
        help="Version to generate content for (e.g., 2.0.0)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="release_body.md",
        help="Output file path (default: release_body.md)",
    )
    parser.add_argument(
        "--release-file",
        default="RELEASE.md",
        help="Path to RELEASE.md file (default: RELEASE.md)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of writing to file",
    )

    args = parser.parse_args()

    # Generate release content
    content = get_release_content(args.version, args.release_file)

    if args.stdout:
        print(content)
        return 0

    # Write to output file
    output_path = Path(args.output)
    try:
        output_path.write_text(content, encoding="utf-8")
        print(f"Release content written to: {output_path}")
        return 0
    except Exception as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
