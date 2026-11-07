"""Snake SURGE 3D center alignment tool launcher."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "tests" / "align_snake.py"), run_name="__main__")
