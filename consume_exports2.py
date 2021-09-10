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
from typing import List, Iterator, Dict
from dataclasses import dataclass


@dataclass
class Document(object):
    id: str
    action: str
    payload: str
    base: bool = False


class Exports(object):
    regex_timestamp = re.compile(r"\d+")

    def __init__(self, path="exports"):
        self.path = path
        self.files = os.listdir(path)
        self.files.sort(key=lambda name: self.regex_timestamp.search(name).group())
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.files)

    def documents(self) -> Iterator[List[Document]]:
        for filename in self:
            yield get_export_docs(os.path.join(self.path, filename))



def get_export_docs(fname) -> List[Document]:
    """Get all the docs from the linewise JSON export file.

    Args:
        * fname (str) export file name.
    Returns:
        All the docs, as dicts (iterable).
    """
    docs = []
    base = "base_" in fname
    with open(fname) as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            doc = Document(**data, base=base)
            docs.append(doc)
    return docs


class Updater(object):
    # Document store. Usually we would use a Postgres database, but that would
    # be total overkill here. So we go with the global, which is unacceptable
    # for production code, of course.
    #     doc["id"] -> doc["payload"]
    docs: Dict[str, str]

    def __init__(self):
        self.docs = dict()
        self.actions = {
            "insert": self.insert,
            "update": self.update,
            "delete": self.delete,
        }
    
    def insert(self, doc: Document):
        if doc.id in self.docs:
            raise KeyError(f"document {doc.id} already exists")
        self.docs[doc.id] = doc.payload

    def update(self, doc: Document):
        if not doc.id in self.docs:
            raise KeyError(f"document {doc.id} does not exist")
        self.docs[doc.id] = doc.payload

    def delete(self, doc: Document):
        if doc.id in self.docs:
            del self.docs[doc.id]

    def update_batch(self, docs: List[Document]):
        if docs and docs[0].base:
            self.docs.clear()
        for doc in docs:
            self.actions[doc.action](doc)
        print("DOCS:", self.docs)

