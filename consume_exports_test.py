#!/usr/bin/env python3
from consume_exports import (
    get_sorted_export_files,
    get_next_export,
    get_export_docs,
    apply_base,
    apply_delta,
    updater,
    DOCS,
)


def test_get_sorted_export_files():
    files = get_sorted_export_files()
    expected = [
        "base_20210401120000.json",
        "delta_20210401130000.json",
        "delta_20210401180000.json",
        "delta_20210401194000.json",
        "delta_20210401233000.json",
        "base_20210402120000.json",
        "delta_20210402180000.json",
    ]
    assert files == expected


def test_get_next_export():
    exports = get_sorted_export_files()
    # without last export the first should be returned
    next_export = get_next_export(exports, last_export=None)
    assert next_export == "base_20210401120000.json"
    # the next file with the greater timestamp should be returned
    # regardless if it is a base or delta file
    next_export = get_next_export(exports, last_export="delta_20210401233000.json")
    assert next_export == "base_20210402120000.json"
    # the last file has no next
    next_export = get_next_export(exports, last_export="delta_20210402180000.json")
    assert next_export == None
    # should this raise an error? no definiton how to handle edge cases
    next_export = get_next_export(exports, last_export="delta_666.json")
    assert next_export == None


def test_get_export_docs():
    # multiple docs in one file with blank lines
    docs = get_export_docs("base_20210401120000.json")
    assert len(docs) == 4
    assert docs[0] == {
        "id": "0",
        "action": "insert",
        "payload": "Doc 0, Stand 2021-04-01 12:00:00",
    }
    assert docs[1] == {
        "id": "1",
        "action": "insert",
        "payload": "Doc 1, Stand 2021-04-01 12:00:00",
    }
    assert docs[2] == {
        "id": "2",
        "action": "insert",
        "payload": "Doc 2, Stand 2021-04-01 12:00:00",
    }
    assert docs[3] == {
        "id": "3",
        "action": "insert",
        "payload": "Doc 3, Stand 2021-04-01 12:00:00",
    }
    # exactly one doc
    docs = get_export_docs("delta_20210401180000.json")
    assert len(docs) == 1
    assert docs[0] == {
        "id": "3",
        "action": "delete",
        "payload": "Doc 3, should never happen! Stand 2021-04-01 18:00:00",
    }


def test_apply_base():
    assert DOCS == {}
    # first batch of base documents
    apply_base("base_20210401120000.json")
    expected = {
        "0": "Doc 0, Stand 2021-04-01 12:00:00",
        "1": "Doc 1, Stand 2021-04-01 12:00:00",
        "2": "Doc 2, Stand 2021-04-01 12:00:00",
        "3": "Doc 3, Stand 2021-04-01 12:00:00",
    }
    assert DOCS == expected
    # next set of base documents
    apply_base("base_20210402120000.json")
    expected = {
        "0": "Doc 0, Stand 2021-04-02 12:00:00",
        "1": "Doc 1, Stand 2021-04-02 12:00:00",
        "2": "Doc 2, Stand 2021-04-02 12:00:00",
        "3": "Doc 3, Stand 2021-04-02 12:00:00",
    }
    assert DOCS == expected


def test_apply_delta():
    DOCS.clear()
    apply_base("base_20210401120000.json")
    # update existing doc
    apply_delta("delta_20210401130000.json")
    expected = {
        "0": "Doc 0, Stand 2021-04-01 13:00:00",
        "1": "Doc 1, Stand 2021-04-01 12:00:00",
        "2": "Doc 2, Stand 2021-04-01 12:00:00",
        "3": "Doc 3, Stand 2021-04-01 12:00:00",
    }
    assert DOCS == expected
    # delete existing doc
    apply_delta("delta_20210401180000.json")
    expected = {
        "0": "Doc 0, Stand 2021-04-01 13:00:00",
        "1": "Doc 1, Stand 2021-04-01 12:00:00",
        "2": "Doc 2, Stand 2021-04-01 12:00:00",
    }
    assert DOCS == expected
    # delete not-existing doc
    apply_delta("delta_20210401180000.json")
    expected = {
        "0": "Doc 0, Stand 2021-04-01 13:00:00",
        "1": "Doc 1, Stand 2021-04-01 12:00:00",
        "2": "Doc 2, Stand 2021-04-01 12:00:00",
    }
    assert DOCS == expected
    # insert new doc
    apply_delta("delta_20210401194000.json")
    expected = {
        "0": "Doc 0, Stand 2021-04-01 13:00:00",
        "1": "Doc 1, Stand 2021-04-01 12:00:00",
        "2": "Doc 2, Stand 2021-04-01 12:00:00",
        "4": "Doc 4, Stand 2021-04-01 19:40:00",
    }
    assert DOCS == expected

def test_updater():
    DOCS.clear()
    files = get_sorted_export_files()
    updater(files)
    expected = {
        "0": "Doc 0, Stand 2021-04-02 12:00:00",
        "1": "Doc 1, Stand 2021-04-02 12:00:00",
        "2": "Doc 2, Stand 2021-04-02 12:00:00",
        "3": "Doc 3, Stand 2021-04-02 12:00:00",
    }
    assert DOCS == expected
