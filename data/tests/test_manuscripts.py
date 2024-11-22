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
