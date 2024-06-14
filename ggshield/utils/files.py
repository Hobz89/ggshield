from enum import Enum, auto
from pathlib import Path, PurePosixPath
from typing import List, Pattern, Set, Union

from ggshield.utils._binary_extensions import BINARY_EXTENSIONS
from ggshield.utils.git_shell import (
    get_filepaths_from_ref,
    git_ls,
    git_ls_unstaged,
    is_git_dir,
)


class ListFilesMode(Enum):
    """
    Control `get_filepaths()` behavior:

    - FILES_ONLY: list specified paths. Expect them to be plain files, raise an exception if one of them is not.
    - ALL: list all specified paths. If one of the path is a directory, list all its paths recursively.
    - ALL_BUT_GITIGNORED: like ALL, except those ignored by git (listed in .gitignore).
    - GIT_COMMITTED_OR_STAGED: list all committed files and all staged files.
    - GIT_COMMITTED: list only committed files.
    """

    FILES_ONLY = auto()
    GIT_COMMITTED = auto()
    GIT_COMMITTED_OR_STAGED = auto()
    ALL_BUT_GITIGNORED = auto()
    ALL = auto()


class UnexpectedDirectoryError(ValueError):
    """Raise when a directory is used where it is not excepted"""

    def __init__(self, path: Path):
        self.path = path


def is_path_excluded(
    path: Union[str, Path], exclusion_regexes: Set[Pattern[str]]
) -> bool:
    path = Path(path)
    if path.is_dir():
        # The directory exclusion regexes have to end with a slash
        # To check if path is excluded, we need to add a trailing slash
        path_string = f"{PurePosixPath(path)}/"
    else:
        path_string = str(PurePosixPath(path))
    return any(r.search(path_string) for r in exclusion_regexes)


def get_filepaths(
    paths: List[Path],
    exclusion_regexes: Set[Pattern[str]],
    list_files_mode: ListFilesMode,
) -> Set[Path]:
    """
    Retrieve the filepaths from the command.

    :param paths: List of file/dir paths from the command
    :param ignore_git: Ignore that the folder is a git repository
    :raise: UnexpectedDirectoryError if directory is given without --recursive option
    """
    targets: Set[Path] = set()
    for path in paths:
        if path.is_file():
            targets.add(path)
        elif path.is_dir():
            if list_files_mode == ListFilesMode.FILES_ONLY:
                raise UnexpectedDirectoryError(path)

            _targets = set()
            if list_files_mode != ListFilesMode.ALL and is_git_dir(path):
                target_filepaths = (
                    get_filepaths_from_ref("HEAD", wd=path)
                    if list_files_mode == ListFilesMode.GIT_COMMITTED
                    else git_ls(path)
                )
                _targets = {path / x for x in target_filepaths}
                if list_files_mode == ListFilesMode.ALL_BUT_GITIGNORED:
                    _targets.update({path / x for x in git_ls_unstaged(path)})
            else:
                _targets = path.rglob(r"*")

            for file_path in _targets:
                if not is_path_excluded(file_path, exclusion_regexes):
                    targets.add(file_path)
    return targets


def is_path_binary(path: Union[str, Path]) -> bool:
    ext = Path(path).suffix
    # `[1:]` because `ext` starts with a "." but extensions in `BINARY_EXTENSIONS` do not
    return ext[1:] in BINARY_EXTENSIONS
