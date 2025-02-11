import pytest
import data.manuscripts as ms
import data.db_connect as dbc
from bson import ObjectId

# Connect to the database
dbc.connect_db()

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


# # Add this fixture at the top of the test file
# @pytest.fixture(autouse=True)
# def setup_test_db():
#     """
#     Set up test database before each test and clean up after
#     """
#     dbc.client[dbc.JOURNAL_DB][ms.MANUSCRIPTS_COLLECTION].drop()
#     yield
#     dbc.client[dbc.JOURNAL_DB][ms.MANUSCRIPTS_COLLECTION].drop()

# TEST_TITLE = "TEST TITLE"
# TEST_AUTHOR = "TEST AUTHOR"
# TEST_AUTHOR_EMAIL = "test@tester.com"
# TEST_TEXT = "TEST CONTENT TEST CONTENT TEST CONTENT"
# TEST_ABSTRACT = "TEST ABSTRACT"

# def test_get_collection_name():
#     """Test that collection name is consistent"""
#     assert ms.get_collection_name() == ms.MANUSCRIPTS_COLLECTION
#     assert ms.get_collection_name(testing=True) == ms.MANUSCRIPTS_COLLECTION


# def test_create_manuscript():
#     """Test manuscript creation"""
#     try:
#         manuscript = ms.create_manuscript(
#             title=TEST_TITLE,
#             author=TEST_AUTHOR,
#             author_email=TEST_AUTHOR_EMAIL,
#             text=TEST_TEXT,
#             abstract=TEST_ABSTRACT
#         )
        
#         assert manuscript[ms.TITLE] == TEST_TITLE
#         assert manuscript[ms.AUTHOR] == TEST_AUTHOR
#         assert manuscript[ms.AUTHOR_EMAIL] == TEST_AUTHOR_EMAIL
#         assert manuscript[ms.STATE] == ms.STATE_SUBMITTED
#         assert manuscript[ms.HISTORY][0]['state'] == ms.STATE_SUBMITTED
#         assert manuscript[ms.HISTORY][0]['actor'] == TEST_AUTHOR_EMAIL
#         assert "_id" in manuscript

#         # Verify in database
#         retrieved = ms.get_manuscript(manuscript["_id"])
#         assert retrieved is not None
#         assert retrieved[ms.TITLE] == TEST_TITLE

#     finally:
#         # Cleanup
#         if manuscript and "_id" in manuscript:
#             ms.delete_manuscript(manuscript["_id"])


# def test_get_manuscript():
#     # Create a manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )

#     # Retrieve the manuscript by ID
#     retrieved = ms.get_manuscript(str(manuscript["_id"]))

#     # Verify the retrieved manuscript matches the created one
#     assert retrieved is not None
#     assert retrieved[ms.TITLE] == TEST_TITLE
#     assert retrieved[ms.AUTHOR] == TEST_AUTHOR
#     assert retrieved[ms.AUTHOR_EMAIL] == TEST_AUTHOR_EMAIL
#     assert retrieved[ms.STATE] == ms.STATE_SUBMITTED

#     # Cleanup
#     ms.delete_manuscript(str(manuscript["_id"]))


# def test_create_manuscript_missing_title():
#     manuscript = ms.create_manuscript(
#         title="",
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
#     assert manuscript[ms.TITLE] == ""


# def test_update_state():
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     # Update state
#     new_state = ms.STATE_AUTHOR_REVISIONS
#     updated_manuscript = ms.update_state(str(manuscript["_id"]), new_state, TEST_AUTHOR_EMAIL)
    
#     # Verify the state has been updated
#     assert updated_manuscript[ms.STATE] == new_state
#     assert updated_manuscript[ms.HISTORY][-1]['state'] == new_state

#     # Cleanup
#     ms.delete_manuscript(str(manuscript["_id"]))


# def test_delete_manuscript():
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     # Delete manuscript
#     deleted_manuscript = ms.delete_manuscript(str(manuscript["_id"]))
    
#     # Verify manuscript was deleted
#     assert deleted_manuscript is not None
#     assert str(manuscript["_id"]) not in ms.get_all_manuscripts()


# def test_invalid_state_transition():
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )

#     # Attempt an invalid state transition
#     invalid_state = "INVALID_STATE"
#     updated_manuscript = ms.update_state(str(manuscript["_id"]), invalid_state, TEST_AUTHOR_EMAIL)
    
#     # Verify the state has not changed
#     assert updated_manuscript is None

#     # Cleanup
#     ms.delete_manuscript(str(manuscript["_id"]))


# def test_update_nonexistent_manuscript():
#     # Attempt to update a non-existent manuscript
#     nonexistent_id = "64d1e69e8f2b3c44b3e3d9c0"
#     updated_manuscript = ms.update_state(nonexistent_id, ms.STATE_REFEREE_REVIEW, TEST_AUTHOR_EMAIL)
#     assert updated_manuscript is None


# def test_assign_referee():
#     """Test assigning a referee to a manuscript"""
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     referee_email = "referee@test.com"
#     updated = ms.assign_referee(str(manuscript["_id"]), referee_email)
    
#     assert updated is not None
#     assert referee_email in updated[ms.REFEREES]
    
#     # Cleanup
#     ms.delete_manuscript(str(manuscript["_id"]))


# def test_remove_referee():
#     """Test removing a referee from a manuscript"""
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     referee_email = "referee@test.com"
#     ms.assign_referee(str(manuscript["_id"]), referee_email)
#     updated = ms.remove_referee(str(manuscript["_id"]), referee_email)
    
#     assert updated is not None
#     assert referee_email not in updated[ms.REFEREES]
    
#     # Cleanup
#     ms.delete_manuscript(str(manuscript["_id"]))


# def test_submit_author_approval():
#     """Test author approval submission"""
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     manuscript_id = str(manuscript["_id"])
    
#     # First move to AUTHOR_REVIEW state
#     ms.update_state(manuscript_id, ms.STATE_AUTHOR_REVIEW, "editor@test.com")
    
#     # Get updated manuscript after state change
#     manuscript = ms.get_manuscript(manuscript_id)
#     assert manuscript[ms.STATE] == ms.STATE_AUTHOR_REVIEW
    
#     # Test approval
#     updated = ms.submit_author_approval(manuscript_id, TEST_AUTHOR_EMAIL)
    
#     assert updated is not None
#     assert updated[ms.STATE] == ms.STATE_FORMATTING
    
#     # Cleanup
#     ms.delete_manuscript(manuscript_id)


# def test_complete_formatting():
#     """Test completing manuscript formatting"""
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     manuscript_id = str(manuscript["_id"])
    
#     # Move to FORMATTING state
#     ms.update_state(manuscript_id, ms.STATE_FORMATTING, "editor@test.com")
    
#     # Get updated manuscript after state change
#     manuscript = ms.get_manuscript(manuscript_id)
#     assert manuscript[ms.STATE] == ms.STATE_FORMATTING
    
#     # Test completing formatting
#     updated = ms.complete_formatting(manuscript_id, "editor@test.com")
    
#     assert updated is not None
#     assert updated[ms.STATE] == ms.STATE_PUBLISHED
    
#     # Cleanup
#     ms.delete_manuscript(manuscript_id)


# def test_complete_copy_edit():
#     """Test completing copy editing"""
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     manuscript_id = str(manuscript["_id"])
    
#     # Move to COPY_EDIT state
#     ms.update_state(manuscript_id, ms.STATE_COPY_EDIT, "editor@test.com")
    
#     # Get updated manuscript after state change
#     manuscript = ms.get_manuscript(manuscript_id)
#     assert manuscript[ms.STATE] == ms.STATE_COPY_EDIT
    
#     # Test completing copy edit
#     updated = ms.complete_copy_edit(manuscript_id, "editor@test.com")
    
#     assert updated is not None
#     assert updated[ms.STATE] == ms.STATE_AUTHOR_REVIEW
    
#     # Cleanup
#     ms.delete_manuscript(manuscript_id)


# def test_validate_state_transition():
#     """Test state transition validation"""
#     # Test valid transitions
#     assert ms.validate_state_transition(
#         ms.STATE_SUBMITTED, 
#         ms.STATE_REFEREE_REVIEW
#     ) is True
#     assert ms.validate_state_transition(
#         ms.STATE_REFEREE_REVIEW, 
#         ms.STATE_AUTHOR_REVISIONS
#     ) is True
#     assert ms.validate_state_transition(
#         ms.STATE_AUTHOR_REVIEW, 
#         ms.STATE_FORMATTING
#     ) is True
    
#     # Test invalid transitions
#     assert ms.validate_state_transition(
#         ms.STATE_SUBMITTED, 
#         ms.STATE_PUBLISHED
#     ) is False
#     assert ms.validate_state_transition(
#         ms.STATE_AUTHOR_REVIEW, 
#         ms.STATE_REFEREE_REVIEW
#     ) is False


# def test_add_referee_report():
#     """Test adding a referee report"""
#     # Create manuscript
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     manuscript_id = str(manuscript["_id"])
#     referee_email = "referee@test.com"
#     report = "This is a test report"
    
#     # First assign referee
#     ms.assign_referee(manuscript_id, referee_email)
    
#     # Test adding report with valid verdict
#     updated = ms.add_referee_report(
#         manuscript_id,
#         referee_email,
#         report,
#         ms.VERDICT_ACCEPT
#     )
    
#     assert updated is not None
#     assert referee_email in updated[ms.REFEREES]
#     assert updated[ms.REFEREES][referee_email][ms.REPORT] == report
#     assert updated[ms.REFEREES][referee_email][ms.VERDICT] == ms.VERDICT_ACCEPT
    
#     # Test invalid verdict
#     with pytest.raises(ValueError):
#         ms.add_referee_report(
#             manuscript_id,
#             referee_email,
#             report,
#             "INVALID_VERDICT"
#         )
    
#     # Cleanup
#     ms.delete_manuscript(manuscript_id)


# def test_state_transitions_with_validation():
#     """Test state transitions with validation"""
#     manuscript = ms.create_manuscript(
#         title=TEST_TITLE,
#         author=TEST_AUTHOR,
#         author_email=TEST_AUTHOR_EMAIL,
#         text=TEST_TEXT,
#         abstract=TEST_ABSTRACT
#     )
    
#     # Test complete workflow path
#     states = [
#         ms.STATE_REFEREE_REVIEW,
#         ms.STATE_AUTHOR_REVISIONS,
#         ms.STATE_COPY_EDIT,
#         ms.STATE_AUTHOR_REVIEW,
#         ms.STATE_FORMATTING,
#         ms.STATE_PUBLISHED
#     ]
    
#     current_id = str(manuscript["_id"])
#     for state in states:
#         updated = ms.update_state(current_id, state, "editor@test.com")
#         assert updated is not None
#         assert updated[ms.STATE] == state
        
#     # Cleanup
#     ms.delete_manuscript(current_id)
