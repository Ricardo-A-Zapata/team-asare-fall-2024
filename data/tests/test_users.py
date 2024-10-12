import pytest

import data.users as usrs


def test_read():
    users = usrs.read()
    assert isinstance(users, dict)
    assert len(users) > 0  # at least one user!
    # keys are user email
    for email, user in users.items():
        assert isinstance(email, str)
        assert len(email) >= usrs.MIN_USER_NAME_LEN
        assert usrs.NAME in user
        assert usrs.EMAIL in user
        assert usrs.AFFILIATION in user


ADD_EMAIL = 'joe@nyu.edu'


def test_create():
    users = usrs.read()
    assert ADD_EMAIL not in users
    usrs.create('Joe Shmoe', ADD_EMAIL, 'NYU')
    users = usrs.read()
    assert ADD_EMAIL in users


BEFORE_NAME = 'before name'
AFTER_NAME = 'after name'
UPDATE_EMAIL = 'update@test.com'
def test_update():
    usrs.create(BEFORE_NAME, UPDATE_EMAIL, 'NYU')
    users = usrs.read()
    assert UPDATE_EMAIL in users
    assert BEFORE_NAME == users[UPDATE_EMAIL][usrs.NAME]
    usrs.update(AFTER_NAME, UPDATE_EMAIL, 'University')
    assert BEFORE_NAME not in users
    assert AFTER_NAME  == users[UPDATE_EMAIL][usrs.NAME]


def test_delete():
    users = usrs.read()
    assert ADD_EMAIL in users
    usrs.delete(ADD_EMAIL)
    users = usrs.read()
    assert ADD_EMAIL not in users


def test_create_duplicate():
    with pytest.raises(ValueError):
        usrs.create('Do not care about name', usrs.TEST_EMAIL, 'Or affiliation')
