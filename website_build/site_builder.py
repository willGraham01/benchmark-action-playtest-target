from pathlib import Path
import shutil

import pandas as pd

from _paths import DEFAULT_BUILD_DIR
from _paths import INDEX_PAGE, PROFILING_LOOKUP_TEMPLATE
from filename_information import git_event, git_SHA
from git_tree import branch_contents, file_contents
from pyis_to_html import pyis_to_html
from utils import clean_build_directory, create_dump_folder, write_md_link

TABLE_EXTRA_COLUMNS = [
    "HTML",
    "Link",
    "Commit",
    "Triggered by",
    "SHA",
]
MARKDOWN_REPLACEMENT_STRING = "<<<MATCH_PATTERN_FOR_MARKDOWN_TABLE_INSERT>>>"


class WebsiteBuilder:
    """
    Handles the construction of the gh-pages website,
    by building the source files from the pyisession files that the source branch contains.
    """

    # If True, the contents of the build directory will be removed before building again.
    # Only works if the build directory lies within (a subdirectory of) the repository root.
    clean_build: bool

    df: pd.DataFrame

    # Repository branch on which source .pyisession files are located.
    source_branch: str
    # Directory to write website files to.
    build_dir: Path
    # Dump folder for temporary files
    dump_folder: Path

    # If True, directory structure of the source files will be ignored,
    # and the build directory will be flat.
    flatten_paths: bool

    def __init__(
        self,
        source_branch: str,
        clean_build: bool = False,
        build_dir: Path = DEFAULT_BUILD_DIR,
        flatten_paths: bool = True,
    ) -> None:
        """
        Initialise the builder by providing the branch the pyis files are stored,
        and build parameters.

        :param source_branch: Branch of the git repo on which pyis files are stored.
        :param clean_build: Purge build directory of its contents before beginning.
        :param build_dir: The directory to write the website files to.
        :param flatten_paths: If True, the directory structure of the source branch will be ignored, and the build directory will be flat.
        """
        pyis_files = branch_contents(source_branch, "*.pyisession")

        self.df = pd.DataFrame({"pyis", pyis_files})
        # Add extra columns to the dataframe, to be populated later
        for col in TABLE_EXTRA_COLUMNS:
            self.df[col] = None

        self.build_dir = build_dir
        self.clean_build = clean_build
        if self.clean_build:
            clean_build_directory(self.build_dir)
        self.flatten_paths = flatten_paths

        # Create the dump folder (and build directory if needed)
        self.dump_folder = create_dump_folder(self.build_dir)

        # Populate information that can be inferred by examining the filenames
        self._infer_filename_information()
        return

    def _infer_filename_information(self) -> None:
        """
        Infer information about the profiling runs by examining the filenames the
        pyis sessions are saved under.

        Filenames are assumed to obey the convention described in filename_information.py.
        """
        # Determine SHA and commit hashes
        self.df[["SHA", "Commit"]] = self.df["pyis"].apply(git_SHA).apply(pd.Series)

        # Workflow event trigger
        self.df["Triggered by"] = self.df["pyis"].apply(git_event)

        return

    def write_pyis_to_html(self):
        """
        Render the HTML output of all pyis files on the source branch,
        writing the outputs to the build directory.

        Updates the site DataFrame to keep track of which HTML file corresponds
        to which pyis file.
        """

        # Render each file to HTML, and save to the output directory
        unique_ID = 0
        for index in self.df.index:
            pyis_file = Path(self.df["pyis"][index])
            dump_file = self.dump_folder / pyis_file
            # Fetch the relevant pyis file from the source branch
            file_contents(self.source_branch, pyis_file, dump_file)

            # Create HTML file name
            if self.flatten_paths:
                html_file_name = self.build_dir / f"{pyis_file.stem}_{unique_ID}.html"
                unique_ID += 1
            else:
                html_file_name = (
                    self.build_dir / f"{pyis_file.parent}" / f"{pyis_file.stem}.html"
                )

            # Render HTML from the pulled pyis session
            pyis_to_html(dump_file, html_file_name)

            # Populate the df entry with the HTML output corresponding to this pyis session
            self.df["HTML"][index] = html_file_name

        # Create clickable markdown links in the Links column
        self.df["Link"] = self.df["HTML"].apply(
            write_md_link, relative_to=self.build_dir, link_text="Profiling results"
        )
        return

    def write_profiling_lookup_table(self) -> str:
        """
        Create the markdown source for the profiling results lookup table,
        by extracting the relevant columns from the DataFrame.
        """
        COLS_FOR_LOOKUP_TABLE = [
            "Link",
            "Commit",
            "Triggered by",
            "SHA",
        ]
        markdown_table = self.df[COLS_FOR_LOOKUP_TABLE].to_markdown()

        # Write the lookup page
        lookup_table_page = self.build_dir / "profiling_index.md"
        with open(PROFILING_LOOKUP_TEMPLATE, "r") as f:
            lookup_page_contents = f.read()
        template_contents = lookup_page_contents.split(MARKDOWN_REPLACEMENT_STRING)
        # Write processed lookup page to the build directory
        with open(lookup_table_page, "w") as f:
            f.write(template_contents[0])
        with open(lookup_table_page, "a") as f:
            f.write(markdown_table)
        with open(lookup_table_page, "a") as f:
            f.write(template_contents[1])
        return

    def write_run_stats(self):
        """ """
        pass

    def build(self) -> None:
        """
        Build the website source files and populate the site DataFrame.
        """
        # Infer additional run stats from the pyis files
        self.write_run_stats()

        # Build the HTML files for the profiling outputs
        self.write_pyis_to_html()

        # Build the lookup page for navigating profiling run outputs
        self.write_profiling_lookup_table()

        # Move index page source file into the build directory
        shutil.copy(INDEX_PAGE, self.build_dir / "index.md")

        # Cleanup the dump folder
        shutil.rmtree(self.dump_folder)
        return
