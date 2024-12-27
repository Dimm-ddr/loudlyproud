#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path

def main():
    tools_dir = Path(__file__).parent

    # Add .tools directory to Python path
    sys.path.insert(0, str(tools_dir))

    # Run tests
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        str(tools_dir / "tags" / "tests"),
        "-vv",
        "--tb=short",
        "--cov=.tools/tags",
        "--cov-report=term-missing",
        "--cov-branch"
    ])

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())