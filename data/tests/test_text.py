import pytest

import data.text as txt

CREATE_KEY = "create"
CREATE_TITLE = "createTitle"
CREATE_TEXT = "createText"


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    for key in texts:
        assert isinstance(key, str)


def test_read_one():
    assert len(txt.read_one(txt.TEST_KEY)) > 0


def test_update():
    pass


def test_delete():
    # check if entry exists
    entry = txt.DEL_KEY
    assert entry in txt.text_dict
    # delete entry
    result = txt.delete(entry)
    # return True if deleted successfully
    assert result is True
    assert entry not in txt.text_dict

def test_create():
    text = txt.read()
    assert CREATE_KEY not in text
    txt.create(CREATE_KEY, CREATE_TITLE, CREATE_TEXT)
    text = txt.read()
    assert CREATE_KEY in text