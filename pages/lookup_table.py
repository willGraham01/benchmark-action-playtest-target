import os
from pathlib import Path
from typing import Tuple

from git_tree import REPO
import pandas as pd

COLS_FOR_TABLE = [
    "Link",
    "Commit",
    "Triggered by",
    "SHA",
]


def write_link(link: Path, relative_to: Path = None, link_text: str = "LINK") -> str:
    """
    Create a markdown hyperlink of the form
    [link_text](HyperLink)

    where the HyperLink points to the file link relative to the relative_to path.
    """
    if relative_to is not None:
        hyperlink = os.path.relpath(link, relative_to)
    else:
        hyperlink = str(link)
    return f"[{link_text}]({hyperlink})"


def git_SHA(fname: Path) -> Tuple[str, str]:
    """
    Extract the git commit SHA and hash, given an pyis session file.

    The pyis filename is used to infer the name of the corresponding meta-file, or the metadata itself.
    """
    # Commit SHA is stored as the "last part" of the filename in this case;
    # path/to/file/{GH_EVENT}_{GH_ID}_{GH_SHA}.extension
    sha = fname.stem.split("_")[-1]
    hash = REPO.git.rev_parse("--short", sha)
    return sha, hash


def git_event(fname: Path) -> str:
    """
    Extract the name of the git event that triggered the profiling run.
    """
    # Event name is the first part of the filename.
    # workflow_dispatch events introduce a spurious underscore, so we catch those cases.
    split_name = fname.stem.split("_")
    if split_name[0] != "workflow":
        return split_name[0]
    else:
        return "workflow dispatch"


def write_lookup_table(site_df: pd.DataFrame, build_dir: Path) -> str:
    """"""
    # Create the clickable link in the link column
    site_df["Link"] = site_df["html"].apply(
        write_link, relative_to=build_dir, link_text="Profiling results"
    )

    # Determine SHA and commit hashes
    site_df[["SHA", "Commit"]] = site_df["pyis"].apply(git_SHA).apply(pd.Series)

    # Workflow event trigger
    site_df["Triggered by"] = site_df["pyis"].apply(git_event)

    # Write markdown
    return site_df[COLS_FOR_TABLE].to_markdown(tablefmt="grid")
