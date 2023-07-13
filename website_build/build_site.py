import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil

import pandas as pd

from _paths import DEFAULT_BUILD_DIR as BUILD_DIR
from _paths import INDEX_PAGE, PROFILING_LOOKUP_TEMPLATE
from git_tree import GIT_ROOT
from lookup_table import COLS_FOR_TABLE
from lookup_table import write_lookup_table
from render_html import build_html

DESCRIPTION = (
    "Build the website deployment for the profiling results, "
    "placing the resulting files in the build directory."
)
MARKDOWN_REPLACEMENT_STRING = "<<<MATCH_PATTERN_FOR_MARKDOWN_TABLE_INSERT>>>"


def create_dump_folder() -> Path:
    """
    Creates a temporary folder within the build directory that can be used to
    dump temporary files, then removed once the build process is over.
    """
    dump_folder = (BUILD_DIR / datetime.utcnow().strftime("%Y%m%d%H%M_tmp")).resolve()
    if os.path.exists(dump_folder):
        raise RuntimeError(f"Temporary directory {dump_folder} already exists!")
    else:
        os.makedirs(dump_folder)
    return dump_folder


def clean_build_directory(build_dir: Path) -> None:
    """
    Remove the build directory and any files within in.
    Only works when the build directory is within the repository root.
    """
    if GIT_ROOT not in build_dir.parents:
        raise RuntimeError(
            f"Cannot remove build directory {args.build_dir} as it is outside repository root {GIT_ROOT}, so could be harmful. Please manually clear the build directory."
        )
    elif os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    return


def build_site(
    source_branch: str,
    build_dir: str | Path = BUILD_DIR,
    flatten_paths: bool = True,
    clean_build_dir: bool = False,
):
    """
    Build the website deployment for the profiling results,
    placing the output into the build directory provided.

    :param source_branch: Repository branch on which source .pyisession files are located.
    :param build_dir: Directory to write website files to.
    :param flatten_paths: If True, directory structure of the source files will be ignored, and the build directory will be flat.
    :param clean_build_dir: If True, the contents of the build directory will be removed before building again. Only works if the build directory lies within (a subdirectory of) the repository root.
    """
    if clean_build_dir:
        clean_build_directory(build_dir)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    dump_folder = create_dump_folder()

    pyis_to_html = build_html(source_branch, dump_folder, build_dir, flatten_paths)

    # Initialise DataFrame for creation of lookup table
    site_df = pd.DataFrame.from_dict(pyis_to_html)
    for col in COLS_FOR_TABLE:
        site_df[col] = None

    # Write profiling results lookup page
    profiling_index_page = build_dir / "profiling_index.md"
    # Fetch templated text from source
    with open(PROFILING_LOOKUP_TEMPLATE, "r") as f:
        lookup_page_contents = f.read()
    template_contents = lookup_page_contents.split(MARKDOWN_REPLACEMENT_STRING)
    # Write lookup table into placeholder location
    markdown_table = write_lookup_table(site_df, build_dir)
    # Write processed lookup page to the build directory
    with open(profiling_index_page, "w") as f:
        f.write(template_contents[0])
    with open(profiling_index_page, "a") as f:
        f.write(markdown_table)
    with open(profiling_index_page, "a") as f:
        f.write(template_contents[1])

    # Move index source file into the build directory
    shutil.copy(INDEX_PAGE, build_dir / "index.md")
    return site_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "source_branch",
        type=str,
        help="Branch to pull pyis session files from.",
    )
    parser.add_argument(
        "build_dir",
        nargs="?",
        type=Path,
        default=BUILD_DIR,
        help=f"Directory to write HTML files into. Defaults to {BUILD_DIR}",
    )
    parser.add_argument(
        "-f",
        "--flatten",
        dest="flatten_paths",
        action="store_true",
        help="Flatten the HTML output in the build directory.",
    )
    parser.add_argument(
        "-c",
        "--clean-build",
        dest="clean_build_dir",
        action="store_true",
        help=f"Force-remove the build directory if it exists already. Will NOT execute on build directories outside the repository root, {GIT_ROOT}",
    )

    args = parser.parse_args()
    args.build_dir = Path(os.path.abspath(args.build_dir))

    build_site(**vars(args))
