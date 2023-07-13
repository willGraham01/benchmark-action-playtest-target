import os
from pathlib import Path
from typing import Dict

BENCHMARK_NAMES = {}


def write_benchmark_entry(
    name: str, unit: str, value: int | float, range: int = None, extra: str = None
) -> Dict[str, str | int | float]:
    """
    Produces a dictionary that can be written as a json record for a benchmarking data-entry.
    Dictionary keys and values correspond to those described in a single entry of:
    https://github.com/benchmark-action/github-action-benchmark.
    """
    entry = {
        "name": name,
        "unit": unit,
        "value": value,
    }
    if range is not None:
        entry["range"] = range
    if extra is not None:
        entry["extra"] = extra
    return entry
