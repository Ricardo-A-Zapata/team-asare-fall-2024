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


NO_AT = 'badEmail.com'
NO_LOCAL_NAME = '@gmail.com'
NO_DOMAIN = 'badEmail@.com'
CONSECUTIVE_PERIOD = 'bad..email@gmail.com'
BEGIN_END_PERIOD = '.bademail.@gmail.com'
ILLEGAL_CHARACTER = 'bad:;email@gmail.com'
NO_PERIODS = 'bademail@gmailcom'
SHORT_TLD = 'bademail@gmail.c'


def test_email_no_at():
    assert not usrs.is_valid_email(NO_AT)


def test_email_no_local_name():
    assert not usrs.is_valid_email(NO_LOCAL_NAME)


def test_email_no_domain():
    assert not usrs.is_valid_email(NO_DOMAIN)


def test_consecutive_period():
    assert not usrs.is_valid_email(CONSECUTIVE_PERIOD)


def test_begin_end_period():
    assert not usrs.is_valid_email(BEGIN_END_PERIOD)


def test_illegal_character():
    assert not usrs.is_valid_email(ILLEGAL_CHARACTER)


def test_no_periods():
    assert not usrs.is_valid_email(NO_PERIODS)


def test_short_domain():
    assert not usrs.is_valid_email(SHORT_TLD)


def test_get_masthead():
    mh = usrs.get_masthead()
    assert isinstance(mh, dict)