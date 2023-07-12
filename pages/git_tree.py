import os
import fnmatch
from pathlib import Path
from typing import List

import git

GIT_ROOT = (Path(os.path.abspath(os.path.dirname(__file__))) / "..").resolve()
REPO = git.Repo(GIT_ROOT)


def list_paths(root_tree, path=Path(".")) -> List[str]:
    """
    Return a generator that iterates over all files (with absolute paths)
    recursively, starting in the directory provided on the given tree.
    """
    for blob in root_tree.blobs:
        yield path / blob.name
    for tree in root_tree.trees:
        yield from list_paths(tree, path / tree.name)


def branch_contents(branch_name: str, match_pattern: str = None) -> List[str]:
    """
    List all contents of a given branch in the repository, which match
    the UNIX pattern provided.
    """
    try:
        branch_tree = getattr(REPO.heads, branch_name).commit.tree
    except AttributeError as e:
        raise RuntimeError(f"{branch_name} not found in the REPO") from e

    files = [str(file) for file in list_paths(branch_tree)]

    if match_pattern is not None:
        files = fnmatch.filter(files, match_pattern)
    return files


def file_contents(
    branch_name: str, path_to_file: str | Path, write_to: str | Path = None
) -> str:
    """
    Fetches the file contents and returns them as a string.
    Can be used to retrieve the contents of files on other branches by passing the branch name.
    Contents can be dumped to a file by specifying write_to.
    """
    file_contents = REPO.git.show(f"{branch_name}:{str(path_to_file)}")

    if write_to is not None:
        with open(write_to, "w") as f:
            f.write(file_contents)
    return file_contents
