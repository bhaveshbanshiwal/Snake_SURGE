"""Backward-compatible wrapper routing to kinematics.snake_kinematics."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from kinematics.snake_kinematics import SnakeKinematics

__all__ = ["SnakeKinematics"]
