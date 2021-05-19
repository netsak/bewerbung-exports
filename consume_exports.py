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


def get_sorted_export_files():
    """ Get list of available export files IN CORRECT ORDER, earliest first.
        Files are in the exports/ subdirectory.
        @return list of export files (list of str).
    """
    ...


def get_next_export(*, last_export):
    """ Assuming we have processed `last_export`: which export is next?
        @param last_export (str) Last processed export file, or None.
        @return next export file (str).
    """
    ...


def get_export_docs(fname):
    """ Get all the docs from the linewise JSON export file.
        @param fname (str) export file name.
        @return all the docs, as dicts (iterable).
    """
    ...


# Document store. Usually we would use a Postgres database, but that would
# be total overkill here. So we go with the global, which is unacceptable
# for production code, of course.
#     doc["id"] -> doc["payload"]
DOCS = {}


def apply_base(fname):
    """ Apply the docs from `fname` *base* file to DOCS.
        A base file contains *all* the docs there are.

        @param fname (str) Filename; file contains linewise JSON objects.
    """
    ...


def apply_delta(fname):
    """ Apply the docs from `fname` *delta* file to DOCS.
        A delta file contains only a "diff" of docs that somehow changed.

        @param fname (str) Filename; file contains linewise JSON objects.
    """
    ...


def updater():
    """ Main loop: read and apply all exports, in correct order, so that
        DOCS are up-to-date.
    """
    export = get_next_export(last_export=None)
    while export:
        print("processing export:", export)
        if export.startswith("base_"):
            apply_base(export)
        else:
            apply_delta(export)
        print("DOCS:", DOCS)
        export = get_next_export(last_export=export)
