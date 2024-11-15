import pytest
from unittest import mock
import mongomock
import data.db_connect as db

@pytest.fixture
def mock_mongo():
    with mock.patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
        db.connect_db()
        yield db.client

def test_insert_one(mock_mongo):
    collection = "TEST"
    doc = {"name": "test", "value": 123}
    result = db.insert_one(collection, doc)
    assert result.inserted_id is not None

def test_fetch_one(mock_mongo):
    collection = "TEST"
    doc = {"name": "test", "value": 123}
    db.insert_one(collection, doc)
    result = db.fetch_one(collection, {"name": "test"})
    assert result["name"] == "test"
    assert result["value"] == 123

def test_fetch_one_nonexistent_document(mock_mongo):
    collection = "test_collection"
    result = db.fetch_one(collection, {"name": "Nonexistent"})
    assert result is None