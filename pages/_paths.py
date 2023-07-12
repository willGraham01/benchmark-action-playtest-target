import os
from pathlib import Path

LOCATION_OF_THIS_FILE = Path(os.path.abspath(os.path.dirname(__file__)))

GIT_ROOT = (LOCATION_OF_THIS_FILE / "..").resolve()
DEFAULT_BUILD_DIR = (LOCATION_OF_THIS_FILE / ".." / "build").resolve()
