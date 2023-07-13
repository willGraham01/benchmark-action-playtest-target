import argparse
import os
from pathlib import Path

from _paths import DEFAULT_BUILD_DIR
from git_tree import GIT_ROOT
from site_builder import WebsiteBuilder

DESCRIPTION = (
    "Build the website deployment for the profiling results, "
    "placing the resulting files in the build directory."
)


def build_site(
    source_branch: str,
    clean_build_dir: bool = False,
    build_dir: str | Path = DEFAULT_BUILD_DIR,
    flatten_paths: bool = True,
):
    """
    Build the website deployment for the profiling results,
    placing the output into the build directory provided.

    :param source_branch: Repository branch on which source .pyisession files are located.
    :param build_dir: Directory to write website files to.
    :param flatten_paths: If True, directory structure of the source files will be ignored, and the build directory will be flat.
    :param clean_build_dir: If True, the contents of the build directory will be removed before building again. Only works if the build directory lies within (a subdirectory of) the repository root.
    """
    builder = WebsiteBuilder(source_branch, clean_build_dir, build_dir, flatten_paths)
    builder.build()

    return builder.df


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
        default=DEFAULT_BUILD_DIR,
        help=f"Directory to write HTML files into. Defaults to {DEFAULT_BUILD_DIR}",
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
