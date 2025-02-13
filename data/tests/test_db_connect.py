import pytest
from unittest import mock
import mongomock
import data.db_connect as db

TEST_COLLECTION = "TEST"
TEST_DOC = {"TEST_NAME": "TEST", "TEST_VALUE": 123}
TEST_FILT = {"TEST_NAME": "TEST"}
TEST_NONEXISTENT_FILT = {"TEST_NAME": "DOES_NOT_EXIST"}

@pytest.fixture
def mock_mongo():
    """
    This fixture provides a mock MongoDB client and ensures
    the test collection is clean before each test.
    """
    with mock.patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
        db.connect_db()
        # Clean up any existing test collection
        db.client[db.JOURNAL_DB][TEST_COLLECTION].drop()
        yield db.client

def test_insert_one(mock_mongo):
    result = db.insert_one(TEST_COLLECTION, TEST_DOC)
    assert result.inserted_id is not None

def test_fetch_one(mock_mongo):
    # Insert without specifying _id
    db.insert_one(TEST_COLLECTION, {"TEST_NAME": "TEST", "TEST_VALUE": 123})
    result = db.fetch_one(TEST_COLLECTION, TEST_FILT)
    assert result["TEST_NAME"] == "TEST"
    assert result["TEST_VALUE"] == 123


def test_fetch_one_nonexistent_document(mock_mongo):
    result = db.fetch_one(TEST_COLLECTION, TEST_NONEXISTENT_FILT)
    assert result is None

def test_fetch_one_with_duplicates(mock_mongo):
    db.insert_one(TEST_COLLECTION, {"TEST_NAME": "TEST", "TEST_VALUE": 123})
    db.insert_one(TEST_COLLECTION, {"TEST_NAME": "TEST", "TEST_VALUE": 1234})

    result = db.fetch_one(TEST_COLLECTION, TEST_FILT)

    assert result is not None
    assert result["TEST_NAME"] == "TEST"
    assert result["TEST_VALUE"] == 123

def test_connect_db_cloud_env(mock_mongo, monkeypatch):
    monkeypatch.setenv("CLOUD_MONGO", "1")
    monkeypatch.setenv("JOURNAL_DB_PW", "test_password")
    monkeypatch.setenv("MONGO_USERNAME", "test_user")
    monkeypatch.setenv("MONGO_CLUSTER", "test_cluster.mongodb.net")
    db.client = None
    db.connect_db()
    assert db.client is not None
    assert isinstance(db.client, mongomock.MongoClient)

def test_fetch_all(mock_mongo):
    db.insert_one(TEST_COLLECTION, {"TEST_NAME": "DOC1", "TEST_VALUE": 1})
    db.insert_one(TEST_COLLECTION, {"TEST_NAME": "DOC2", "TEST_VALUE": 2})
    result = db.fetch_all(TEST_COLLECTION)
    assert len(result) == 2
    assert any(doc["TEST_NAME"] == "DOC1" for doc in result)
    assert any(doc["TEST_NAME"] == "DOC2" for doc in result)
