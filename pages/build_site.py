import argparse
from datetime import datetime
import os
from pathlib import Path
from shutil import rmtree
from typing import Dict

from _paths import DEFAULT_BUILD_DIR as BUILD_DIR
from git_tree import branch_contents, file_contents
from git_tree import GIT_ROOT
from render_html import render_html

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


def build_html(
    source_branch: str, build_dir: str | Path = BUILD_DIR, flatten_paths: bool = True
) -> Dict[str, str]:
    """
    Using pyis session files stored on the target branch, build the corresponding
    html pages and place them into the build directory.

    If flatten_paths is true, directory structure will not be preserved.
    Name conflicts will be prevented by appending incremental integers to file names.

    Returns a dictionary of key, value pairs of the form:
    pyis session, name of the html file produced.
    """
    # Fetch all pyis session files on the source branch
    pyis_files = branch_contents(source_branch, "*.pyisession")

    dump_folder = create_dump_folder()
    pyis_to_html = dict()

    # Render each file to HTML, and save to the output directory
    unique_ID = 0
    for pyis_file in [Path(p) for p in pyis_files]:
        # Copy file contents to the dump folder
        dump_file_loc = dump_folder / pyis_file
        file_contents(source_branch, pyis_file, dump_file_loc)

        # Create HTML file name
        if flatten_paths:
            html_file_name = build_dir / f"{pyis_file.stem}_{unique_ID}.html"
            unique_ID += 1
        else:
            html_file_name = (
                build_dir / f"{pyis_file.parent}" / f"{pyis_file.stem}.html"
            )
        # Render HTML from the pulled pyis session
        render_html(dump_file_loc, html_file_name)

        # Append this pairing to the dictionary
        pyis_to_html[str(pyis_file)] = html_file_name

    # Purge temporary directory
    rmtree(dump_folder)

    return pyis_to_html


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

    d = build_html(source_branch, build_dir, flatten_paths)
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
