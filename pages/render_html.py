import os
from pathlib import Path
from shutil import rmtree
from typing import Dict

from pyinstrument.session import Session
from pyinstrument.renderers import HTMLRenderer

from _paths import DEFAULT_BUILD_DIR as BUILD_DIR
from git_tree import branch_contents, file_contents


def render_html(pyis_in: str | Path, html_out: str | Path):
    """
    Renders a pyis session file as HTML for visual output.
    """
    pyi_session = Session.load(pyis_in)
    if not os.path.exists(html_out.parent):
        os.makedirs(html_out.parent)

    renderer = HTMLRenderer(show_all=False, timeline=False)

    print(f"Writing {html_out}", end="...", flush=True)
    with open(html_out, "w") as f:
        f.write(renderer.render(pyi_session))
    print("done")
    return


def build_html(
    source_branch: str,
    dump_folder: Path,
    build_dir: str | Path = BUILD_DIR,
    flatten_paths: bool = True,
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

    pyis_to_html = {
        "pyis": [],
        "html": [],
    }

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
        pyis_to_html["pyis"].append(pyis_file)
        pyis_to_html["html"].append(html_file_name)

    # Purge temporary directory
    rmtree(dump_folder)

    return pyis_to_html
