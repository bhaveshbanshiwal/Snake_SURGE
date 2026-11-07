"""Snake SURGE ST3215 bus diagnostic tool launcher."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "tests" / "diagnose_bus.py"), run_name="__main__")
