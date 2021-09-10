#!/usr/bin/env python3
from consume_exports2 import (
    Exports,
    Updater,
    get_export_docs,
)


def test_Exports():
    files = list(Exports())
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


def test_get_export_docs():
    # multiple docs in one file with blank lines
    docs = get_export_docs("exports/base_20210401120000.json")
    assert len(docs) == 4
    assert docs[0].__dict__ == {
        "id": "0",
        "action": "insert",
        "payload": "Doc 0, Stand 2021-04-01 12:00:00",
        "base": True,
    }
    assert docs[1].__dict__ == {
        "id": "1",
        "action": "insert",
        "payload": "Doc 1, Stand 2021-04-01 12:00:00",
        "base": True,
    }
    assert docs[2].__dict__ == {
        "id": "2",
        "action": "insert",
        "payload": "Doc 2, Stand 2021-04-01 12:00:00",
        "base": True,
    }
    assert docs[3].__dict__ == {
        "id": "3",
        "action": "insert",
        "payload": "Doc 3, Stand 2021-04-01 12:00:00",
        "base": True,
    }
    # exactly one doc
    docs = get_export_docs("exports/delta_20210401180000.json")
    assert len(docs) == 1
    assert docs[0].__dict__ == {
        "id": "3",
        "action": "delete",
        "payload": "Doc 3, should never happen! Stand 2021-04-01 18:00:00",
        "base": False,
    }


def test_update():
    exports = Exports()
    updater = Updater()
    for batch in exports.documents():
        updater.update_batch(batch)
    expected = {
        "0": "Doc 0, Stand 2021-04-02 12:00:00",
        "1": "Doc 1, Stand 2021-04-02 12:00:00",
        "2": "Doc 2, Stand 2021-04-02 12:00:00",
        "3": "Doc 3, Stand 2021-04-02 12:00:00",
    }
    assert updater.docs == expected
