#!/usr/bin/env python3
#
# Consume export files and keep a set of documents up-to-date.
#
# Export files contain linewise JSON (i.e. one JSON object per line).
# Each JSON object is one document and has the following keys:
#
#   doc["id"]: identifier
#   doc["action"]: what to do with the object "insert", "update", or "delete"
#   doc["payload"]: this is the actual payload we want to store
#
import os
import re
import json
from typing import List, Dict


REGEX_TIMESTAMP = re.compile(r"\d+")


def get_sorted_export_files() -> List[str]:
    """Get list of available export files IN CORRECT ORDER, earliest first.
    Files are in the exports/ subdirectory.

    Returns:
        List of export files (list of str).
    """
    # dir_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    files = os.listdir("exports")
    files.sort(key=lambda n: REGEX_TIMESTAMP.search(n).group())
    return files


def get_next_export(exports: List[str], last_export: str) -> str:
    """Assuming we have processed `last_export`: which export is next?

    Args:
        exports (List[str])
        last_export (str) Last processed export file, or None.
    Returns:
        Next export file (str).
    """
    if not last_export:
        return exports[0]
    last_time = REGEX_TIMESTAMP.search(last_export).group()
    for filename in exports:
        if filename == last_export:
            continue
        filename_time = REGEX_TIMESTAMP.search(filename).group()
        if filename_time <= last_time:
            continue
        return filename
    return None


def get_export_docs(fname) -> List[Dict[str, object]]:
    """Get all the docs from the linewise JSON export file.

    Args:
        * fname (str) export file name.
    Returns:
        All the docs, as dicts (iterable).
    """
    docs = []
    with open(os.path.join("exports", fname)) as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            docs.append(data)
    return docs


# Document store. Usually we would use a Postgres database, but that would
# be total overkill here. So we go with the global, which is unacceptable
# for production code, of course.
#     doc["id"] -> doc["payload"]
DOCS = {}


def apply_base(fname):
    """Apply the docs from `fname` *base* file to DOCS.
    A base file contains *all* the docs there are.

    Args:
        * fname (str) Filename; file contains linewise JSON objects.
    """
    DOCS.clear()
    for doc in get_export_docs(fname):
        assert doc["action"] == "insert"
        DOCS[doc["id"]] = doc["payload"]


def apply_delta(fname):
    """Apply the docs from `fname` *delta* file to DOCS.
    A delta file contains only a "diff" of docs that somehow changed.

    Args:
        * fname (str) Filename; file contains linewise JSON objects.
    """
    for doc in get_export_docs(fname):
        if doc["action"] == "insert":
            DOCS[doc["id"]] = doc["payload"]
        elif doc["action"] == "update":
            DOCS[doc["id"]] = doc["payload"]
        elif doc["action"] == "delete":
            if doc["id"] in DOCS:
                del DOCS[doc["id"]]
        else:
            pass  # other extions are ignored


def updater(exports):
    """Main loop: read and apply all exports, in correct order, so that
    DOCS are up-to-date.
    """
    export = get_next_export(exports, last_export=None)
    while export:
        print("processing export:", export)
        if export.startswith("base_"):
            apply_base(export)
        else:
            apply_delta(export)
        print("DOCS:", DOCS)
        export = get_next_export(exports, last_export=export)
