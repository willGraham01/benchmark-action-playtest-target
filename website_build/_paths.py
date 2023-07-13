import os
from pathlib import Path

LOCATION_OF_THIS_FILE = Path(os.path.abspath(os.path.dirname(__file__)))

GIT_ROOT = (LOCATION_OF_THIS_FILE / "..").resolve()

DEFAULT_BUILD_DIR = (LOCATION_OF_THIS_FILE / ".." / "build").resolve()

SRC_DIR = (GIT_ROOT / "src").resolve()
PROFILING_LOOKUP_TEMPLATE = (SRC_DIR / "profiling_index.md").resolve()
INDEX_PAGE = (SRC_DIR / "index.md").resolve()
RUN_STATS_LOOKUP_TEMPLATE = (SRC_DIR / "run_statistics.md").resolve()
