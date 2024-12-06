import pytest
import data.manuscripts as ms

TEST_TITLE = "TEST TITLE"
TEST_AUTHOR = "TEST AUTHOR"
TEST_AUTHOR_EMAIL = "test@tester.com"
TEST_TEXT = "TEST CONTENT TEST CONTENT TEST CONTENT"
TEST_ABSTRACT = "TEST ABSTRACT"

def test_create_manuscript():
    # Call the create_manuscript function
    manuscript = ms.create_manuscript(
        title=TEST_TITLE,
        author=TEST_AUTHOR,
        author_email=TEST_AUTHOR_EMAIL,
        text=TEST_TEXT,
        abstract=TEST_ABSTRACT
    )
    
    # Verify the output
    assert manuscript[ms.TITLE] == TEST_TITLE
    assert manuscript[ms.AUTHOR] == TEST_AUTHOR
    assert manuscript[ms.AUTHOR_EMAIL] == TEST_AUTHOR_EMAIL
    assert manuscript[ms.STATE] == ms.STATE_SUBMITTED
    assert manuscript[ms.HISTORY][0]['state'] == ms.STATE_SUBMITTED
    assert manuscript[ms.HISTORY][0]['actor'] == TEST_AUTHOR_EMAIL
    assert "_id" in manuscript  # Check that _id is present

    # Cleanup after testing
    if "_id" in manuscript:
        ms.delete_manuscript(manuscript["_id"])


def test_get_manuscript():
    # Create a manuscript
    manuscript = ms.create_manuscript(
        title=TEST_TITLE,
        author=TEST_AUTHOR,
        author_email=TEST_AUTHOR_EMAIL,
        text=TEST_TEXT,
        abstract=TEST_ABSTRACT
    )

    # Retrieve the manuscript by ID
    retrieved = ms.get_manuscript(str(manuscript["_id"]))

    # Verify the retrieved manuscript matches the created one
    assert retrieved is not None
    assert retrieved[ms.TITLE] == TEST_TITLE
    assert retrieved[ms.AUTHOR] == TEST_AUTHOR
    assert retrieved[ms.AUTHOR_EMAIL] == TEST_AUTHOR_EMAIL
    assert retrieved[ms.STATE] == ms.STATE_SUBMITTED

    # Cleanup
    ms.delete_manuscript(str(manuscript["_id"]))


def test_create_manuscript_missing_title():
    manuscript = ms.create_manuscript(
        title="",
        author=TEST_AUTHOR,
        author_email=TEST_AUTHOR_EMAIL,
        text=TEST_TEXT,
        abstract=TEST_ABSTRACT
    )
    assert manuscript[ms.TITLE] == ""


def test_update_state():
    # Create manuscript
    manuscript = ms.create_manuscript(
        title=TEST_TITLE,
        author=TEST_AUTHOR,
        author_email=TEST_AUTHOR_EMAIL,
        text=TEST_TEXT,
        abstract=TEST_ABSTRACT
    )
    
    # Update state
    new_state = ms.STATE_AUTHOR_REVISIONS
    updated_manuscript = ms.update_state(str(manuscript["_id"]), new_state, TEST_AUTHOR_EMAIL)
    
    # Verify the state has been updated
    assert updated_manuscript[ms.STATE] == new_state
    assert updated_manuscript[ms.HISTORY][-1]['state'] == new_state

    # Cleanup
    ms.delete_manuscript(str(manuscript["_id"]))


def test_delete_manuscript():
    # Create manuscript
    manuscript = ms.create_manuscript(
        title=TEST_TITLE,
        author=TEST_AUTHOR,
        author_email=TEST_AUTHOR_EMAIL,
        text=TEST_TEXT,
        abstract=TEST_ABSTRACT
    )
    
    # Delete manuscript
    deleted_manuscript = ms.delete_manuscript(str(manuscript["_id"]))
    
    # Verify manuscript was deleted
    assert deleted_manuscript is not None
    assert str(manuscript["_id"]) not in ms.get_all_manuscripts()
    