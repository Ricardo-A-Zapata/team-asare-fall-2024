import pytest
import data.text as txt
import data.db_connect as dbc

CREATE_KEY = "create"
CREATE_TITLE = "createTitle"
CREATE_TEXT = "createText"


@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Set up test database before each test and clean up after
    """
    # Setup
    dbc.client[dbc.JOURNAL_DB][txt.TEST_COLLECTION].drop()
    # Create test text entries
    txt.create(txt.TEST_KEY, 'Home Page',
              'This is a journal about building API servers.',
              testing=True)
    txt.create(txt.SUBM_KEY, 'Submissions Page',
              'All submissions must be original work in Word format.',
              testing=True)
    txt.create(txt.DEL_KEY, 'Delete Page',
              'This is a text to delete.',
              testing=True)
    
    yield
    
    # Teardown
    dbc.client[dbc.JOURNAL_DB][txt.TEST_COLLECTION].drop()


def test_read():
    texts = txt.read(testing=True)
    assert isinstance(texts, dict)
    for key in texts:
        assert isinstance(key, str)
        assert txt.TITLE in texts[key]
        assert txt.TEXT in texts[key]


def test_read_one():
    text = txt.read_one(txt.TEST_KEY, testing=True)
    assert len(text) > 0
    assert txt.TITLE in text
    assert txt.TEXT in text


def test_create():
    text = txt.read(testing=True)
    assert CREATE_KEY not in text
    txt.create(CREATE_KEY, CREATE_TITLE, CREATE_TEXT, testing=True)
    text = txt.read(testing=True)
    assert CREATE_KEY in text
    assert text[CREATE_KEY][txt.TITLE] == CREATE_TITLE
    assert text[CREATE_KEY][txt.TEXT] == CREATE_TEXT


BEFORE_TITLE = 'Old Title'
AFTER_TITLE = 'Updated Title'
UPDATE_KEY = 'update_key'
UPDATE_TEXT = 'Updated text content'


def test_update():
    txt.create(UPDATE_KEY, BEFORE_TITLE, 'Old text content', testing=True)
    texts = txt.read(testing=True)
    assert UPDATE_KEY in texts
    assert BEFORE_TITLE == texts[UPDATE_KEY][txt.TITLE]

    txt.update(UPDATE_KEY, AFTER_TITLE, UPDATE_TEXT, testing=True)
    texts = txt.read(testing=True)
    assert texts[UPDATE_KEY][txt.TITLE] == AFTER_TITLE
    assert texts[UPDATE_KEY][txt.TEXT] == UPDATE_TEXT


def test_delete():
    # check if entry exists
    texts = txt.read(testing=True)
    assert txt.DEL_KEY in texts
    
    # delete entry
    result = txt.delete(txt.DEL_KEY, testing=True)
    
    # return True if deleted successfully
    assert result is True
    texts = txt.read(testing=True)
    assert txt.DEL_KEY not in texts


def test_create_duplicate():
    with pytest.raises(KeyError):
        txt.create(txt.TEST_KEY, 'Duplicate', 'Text', testing=True)
