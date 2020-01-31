"""Functions related to finding modules for testing."""

from collections import defaultdict
import glob
from pathlib import Path
import re
import subprocess


def find_modules(module_path):
    """Find all modules in the module (possibly package) represented by `module_path`.

    Args:
        module_path: A pathlib.Path to a Python package or module.

    Returns: An iterable of paths Python modules (i.e. *py files).
    """
    if module_path.is_file():
        if module_path.suffix == '.py':
            yield module_path
    elif module_path.is_dir():
        pyfiles = glob.glob('{}/**/*.py'.format(module_path), recursive=True)
        yield from (Path(pyfile) for pyfile in pyfiles)


def filter_paths(paths, excluded_paths):
    """Filter out path matching one of excluded_paths glob

    Args:
        paths: path to filter.
        excluded_paths: List for glob of modules to exclude.

    Returns: An iterable of paths Python modules (i.e. *py files).
    """
    excluded = set(Path(f) for excluded_path in excluded_paths
                   for f in glob.glob(excluded_path, recursive=True))
    return set(paths) - excluded

def git_filters(config):
    branch = config.get("git-branch")
    if branch is None:
        return

    # Get the set of new lines by file
    # we could use interlap, but do not want to
    # add new dependency at the moment
    diff = subprocess.run(
        ["git", "diff", "--relative", "-U0", branch, "."],
        capture_output=True)
    regex = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@.*")
    current_file = None
    res = defaultdict(set)
    for diff_line in diff.stdout.decode('utf-8').split('\n'):
        if diff_line.startswith("@@"):
            m = regex.match(diff_line)
            start = int(m.group(1))
            lenght = int(m.group(2)) if m.group(2) is not None else 1
            for line in range(start, start + lenght):
                res[current_file].add(line)
        if diff_line.startswith("+++ b/"):
            current_file = Path(diff_line[6:])
    return res
