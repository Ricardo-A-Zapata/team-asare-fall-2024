import pytest

import data.text as txt

CREATE_KEY = "create"
CREATE_TITLE = "createTitle"
CREATE_TEXT = "createText"

def test_read():
    pass


def test_read_one():
    pass


def test_update():
    pass


def test_delete():
    pass

def test_create():
    text = txt.read()
    assert CREATE_KEY not in text
    txt.create(CREATE_KEY, CREATE_TITLE, CREATE_TEXT)
    text = txt.read()
    assert CREATE_KEY in text