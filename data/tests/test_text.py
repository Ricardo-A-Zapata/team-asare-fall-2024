import pytest

import data.text as txt


def test_read():
    pass


def test_read_one():
    pass


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
