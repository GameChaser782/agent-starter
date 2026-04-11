import os
import tempfile

import pytest

from agent_starter.memory.backends.sqlite import SQLiteBackend
from agent_starter.memory.long_term import SQLiteLongTermMemory


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_memory.db")


def test_sqlite_backend_upsert(db_path):
    backend = SQLiteBackend(db_path)
    backend.upsert("user1", "name", "Alice")
    memories = backend.fetch_all("user1")
    assert len(memories) == 1
    assert memories[0]["key"] == "name"
    assert memories[0]["value"] == "Alice"


def test_sqlite_backend_upsert_updates(db_path):
    backend = SQLiteBackend(db_path)
    backend.upsert("user1", "name", "Alice")
    backend.upsert("user1", "name", "Bob")  # update
    memories = backend.fetch_all("user1")
    assert len(memories) == 1
    assert memories[0]["value"] == "Bob"


def test_sqlite_backend_user_isolation(db_path):
    backend = SQLiteBackend(db_path)
    backend.upsert("user1", "lang", "Python")
    backend.upsert("user2", "lang", "Rust")
    assert backend.fetch_all("user1")[0]["value"] == "Python"
    assert backend.fetch_all("user2")[0]["value"] == "Rust"


def test_sqlite_backend_search(db_path):
    backend = SQLiteBackend(db_path)
    backend.upsert("u1", "preferred_language", "Python")
    backend.upsert("u1", "current_project", "FastAPI REST API")
    results = backend.search("u1", "python language")
    assert len(results) > 0
    assert any(r["key"] == "preferred_language" for r in results)


def test_long_term_memory_store_and_recall(db_path):
    mem = SQLiteLongTermMemory(db_path=db_path)
    mem.store("alice", "hobby", "rock climbing")
    mem.store("alice", "location", "Berlin")
    results = mem.recall("alice", "climbing hobby")
    assert any(r["key"] == "hobby" for r in results)


def test_long_term_memory_summarize(db_path):
    mem = SQLiteLongTermMemory(db_path=db_path)
    mem.store("bob", "role", "data scientist")
    summary = mem.summarize("bob")
    assert "role" in summary
    assert "data scientist" in summary


def test_long_term_memory_empty_user(db_path):
    mem = SQLiteLongTermMemory(db_path=db_path)
    summary = mem.summarize("unknown_user")
    assert summary == ""
