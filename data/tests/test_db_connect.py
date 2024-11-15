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
    with mock.patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
        db.connect_db()
        yield db.client

def test_insert_one(mock_mongo):
    result = db.insert_one(TEST_COLLECTION, TEST_DOC)
    assert result.inserted_id is not None

def test_fetch_one(mock_mongo):
    db.insert_one(TEST_COLLECTION, {"_id": 1, "TEST_NAME": "TEST", "TEST_VALUE": 123})
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
