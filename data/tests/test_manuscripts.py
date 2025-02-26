import pytest
import data.manuscripts as ms
import data.db_connect as dbc
from bson import ObjectId

# Connect to the database
dbc.connect_db()

@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Set up test database before each test and clean up after.
    This fixture runs automatically before and after each test.
    """
    # Clean up before test
    dbc.client[dbc.JOURNAL_DB][ms.MANUSCRIPTS_COLLECTION].delete_many({})
    yield
    # Clean up after test
    dbc.client[dbc.JOURNAL_DB][ms.MANUSCRIPTS_COLLECTION].delete_many({})

def test_create_manuscript():
    manuscript = ms.create_manuscript(
        title="Test Manuscript",
        author="John Doe",
        author_email="johndoe@example.com",
        text="Sample manuscript text",
        abstract="Sample abstract"
    )
    assert manuscript is not None, "Manuscript creation failed."
    assert "_id" in manuscript, "Manuscript does not contain an '_id' field."

    # Ensure manuscripts in the database
    manuscripts = dbc.client['teamasare']['manuscripts']
    manuscript_in_db = manuscripts.find_one({"_id": ObjectId(manuscript["_id"])})
    assert manuscript_in_db is not None, "Manuscript not found in the database."
    assert "manuscripts" in dbc.client['teamasare'].list_collection_names(), "Manuscripts collection not found."

    # Cleanup
    manuscripts.delete_one({"_id": ObjectId(manuscript["_id"])})


def test_update_manuscript_text():
    """Test updating manuscript text with revision tracking"""
    # Create a manuscript
    manuscript = ms.create_manuscript(
        title="Test Manuscript",
        author="John Doe",
        author_email="johndoe@example.com",
        text="Original text",
        abstract="Original abstract"
    )
    
    manuscript_id = str(manuscript["_id"])
    
    try:
        # Update the text
        updated = ms.update_manuscript_text(
            manuscript_id,
            "Updated text",
            "Updated abstract",
            "johndoe@example.com",
            "Response to reviewer comments"
        )
        
        # Verify update
        assert updated is not None
        assert updated[ms.TEXT] == "Updated text"
        assert updated[ms.ABSTRACT] == "Updated abstract"
        assert updated[ms.VERSION] == 2
        assert len(updated[ms.REVISIONS]) == 2
        assert updated[ms.REVISIONS][-1][ms.VERSION] == 2
        assert updated[ms.REVISIONS][-1][ms.TEXT] == "Updated text"
        assert updated[ms.REVISIONS][-1][ms.AUTHOR_RESPONSE] == "Response to reviewer comments"
        
        # Verify history
        assert len(updated[ms.HISTORY]) > 1
        last_history = updated[ms.HISTORY][-1]
        assert last_history["action"] == "text_update"
        assert last_history["version"] == 2
        
    finally:
        # Cleanup
        ms.delete_manuscript(manuscript_id)


def test_get_manuscript_version():
    """Test retrieving specific manuscript versions"""
    # Create a manuscript
    manuscript = ms.create_manuscript(
        title="Test Manuscript",
        author="John Doe",
        author_email="johndoe@example.com",
        text="Original text",
        abstract="Original abstract"
    )
    
    manuscript_id = str(manuscript["_id"])
    
    try:
        # Update the text to create version 2
        ms.update_manuscript_text(
            manuscript_id,
            "Updated text",
            "Updated abstract",
            "johndoe@example.com"
        )
        
        # Get version 1
        version1 = ms.get_manuscript_version(manuscript_id, 1)
        assert version1 is not None
        assert version1[ms.TEXT] == "Original text"
        assert version1[ms.ABSTRACT] == "Original abstract"
        assert version1[ms.VERSION] == 1
        assert version1['current_version'] == 2
        
        # Get version 2
        version2 = ms.get_manuscript_version(manuscript_id, 2)
        assert version2 is not None
        assert version2[ms.TEXT] == "Updated text"
        assert version2[ms.ABSTRACT] == "Updated abstract"
        assert version2[ms.VERSION] == 2
        assert version2['current_version'] == 2
        
        # Try to get non-existent version
        version3 = ms.get_manuscript_version(manuscript_id, 3)
        assert "error" in version3
        
    finally:
        # Cleanup
        ms.delete_manuscript(manuscript_id)


def test_invalid_state_transition():
    """Ensure invalid state transitions return an error message"""
    manuscript = ms.create_manuscript(
        title="Invalid Transition Test",
        author="John Doe",
        author_email="johndoe@example.com",
        text="Manuscript text",
        abstract="Manuscript abstract"
    )

    manuscript_id = str(manuscript["_id"])
    invalid_state = "INVALID_STATE"

    try:
        # Attempt an invalid transition
        response = ms.update_state(manuscript_id, invalid_state, "editor@example.com")
        assert response is not None
        assert "error" in response
    finally:
        ms.delete_manuscript(manuscript_id)


def test_get_all_manuscripts():
    """Test retrieving all manuscripts"""
    # Create multiple manuscripts
    manuscript1 = ms.create_manuscript(
        title="Test Manuscript 1",
        author="John Doe",
        author_email="john@example.com",
        text="Sample text 1",
        abstract="Sample abstract 1"
    )
    
    manuscript2 = ms.create_manuscript(
        title="Test Manuscript 2",
        author="Jane Doe",
        author_email="jane@example.com",
        text="Sample text 2",
        abstract="Sample abstract 2"
    )
    
    try:
        # Get all manuscripts
        all_manuscripts = ms.get_all_manuscripts()
        
        # Verify both manuscripts are retrieved
        assert len(all_manuscripts) >= 2
        assert manuscript1["_id"] in all_manuscripts
        assert manuscript2["_id"] in all_manuscripts
        
        # Verify manuscript contents
        assert all_manuscripts[manuscript1["_id"]]["title"] == "Test Manuscript 1"
        assert all_manuscripts[manuscript2["_id"]]["title"] == "Test Manuscript 2"
        
    finally:
        # Cleanup
        ms.delete_manuscript(manuscript1["_id"])
        ms.delete_manuscript(manuscript2["_id"])


def test_manuscript_multiple_revisions():
    """Test that manuscript properly tracks multiple revisions with version numbers"""
    # Create initial manuscript
    manuscript = ms.create_manuscript(
        title="Version Test Manuscript",
        author="Test Author",
        author_email="test@example.com",
        text="Original text",
        abstract="Original abstract"
    )
    manuscript_id = str(manuscript["_id"])
    
    try:
        # Verify initial version
        assert manuscript[ms.VERSION] == 1
        assert len(manuscript[ms.REVISIONS]) == 1
        assert manuscript[ms.REVISIONS][0][ms.VERSION] == 1
        assert manuscript[ms.REVISIONS][0][ms.TEXT] == "Original text"
        
        # Make first revision
        updated1 = ms.update_manuscript_text(
            manuscript_id,
            "Updated text v2",
            "Updated abstract v2",
            "test@example.com",
            "First revision comments"
        )
        assert updated1[ms.VERSION] == 2
        assert len(updated1[ms.REVISIONS]) == 2
        assert updated1[ms.REVISIONS][1][ms.TEXT] == "Updated text v2"
        assert updated1[ms.REVISIONS][1][ms.AUTHOR_RESPONSE] == "First revision comments"
        
        # Make second revision
        updated2 = ms.update_manuscript_text(
            manuscript_id,
            "Updated text v3",
            "Updated abstract v3",
            "test@example.com",
            "Second revision comments"
        )
        assert updated2[ms.VERSION] == 3
        assert len(updated2[ms.REVISIONS]) == 3
        assert updated2[ms.REVISIONS][2][ms.TEXT] == "Updated text v3"
        assert updated2[ms.REVISIONS][2][ms.AUTHOR_RESPONSE] == "Second revision comments"
        
        # Verify we can retrieve specific versions
        version1 = ms.get_manuscript_version(manuscript_id, 1)
        assert version1[ms.TEXT] == "Original text"
        
        version2 = ms.get_manuscript_version(manuscript_id, 2)
        assert version2[ms.TEXT] == "Updated text v2"
        
        version3 = ms.get_manuscript_version(manuscript_id, 3)
        assert version3[ms.TEXT] == "Updated text v3"
        
        # Verify invalid version returns error
        invalid_version = ms.get_manuscript_version(manuscript_id, 4)
        assert "error" in invalid_version
        
    finally:
        ms.delete_manuscript(manuscript_id)
