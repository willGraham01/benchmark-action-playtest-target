import argparse
from datetime import datetime
import os
from pathlib import Path
from shutil import rmtree
from typing import Dict

from _paths import DEFAULT_BUILD_DIR as BUILD_DIR
from git_tree import GIT_ROOT
from render_html import build_html

DESCRIPTION = (
    "Build the website deployment for the profiling results, "
    "placing the resulting files in the build directory."
)


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
    else:
        rmtree(args.build_dir)
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

    dump_folder = create_dump_folder()

    d = build_html(source_branch, dump_folder, build_dir, flatten_paths)
    return d


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "source", type=str, help="Branch to pull pyis session files from."
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

    df = build_site(**vars(args))
    print(df)
