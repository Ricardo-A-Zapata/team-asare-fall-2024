import pytest

import data.users as usrs

from data.users import NAME, ROLES


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
ADD_AFFILIATION = "NYU"
VALID_ROLE = "AD"
INVALID_ROLE = "InvalidRole"


def test_create():
    users = usrs.read()
    assert ADD_EMAIL not in users, "User should not already exist before creation"
    usrs.create(NAME, ADD_EMAIL, ADD_AFFILIATION, role="AU")
    users = usrs.read()
    assert ADD_EMAIL in users, "User should exist after creation with role"
    assert users[ADD_EMAIL]["roles"] == ["AU"], "User should have role 'AU' (Author) assigned"
    usrs.delete(ADD_EMAIL)


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
    if ADD_EMAIL not in users:
        usrs.create("John Doe", ADD_EMAIL, "NYU")
    users = usrs.read()
    assert ADD_EMAIL in users, "User should exist after creation"
    usrs.delete(ADD_EMAIL)
    users = usrs.read()
    assert ADD_EMAIL not in users, "User should not exist after deletion"


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
LONG_TLD = 'bademail@gmail.commmmmm'
MIXED_CASE = 'Valid.Email@Example.COM'
MIN_LENGTH = 'z@z.co'


def test_email_no_at():
    assert not usrs.is_valid_email(NO_AT)


def test_email_no_local_name():
    assert not usrs.is_valid_email(NO_LOCAL_NAME)


def test_email_no_domain():
    assert not usrs.is_valid_email(NO_DOMAIN)


def test_email_mixed_case():
    assert usrs.is_valid_email(MIXED_CASE)


def test_email_minimum_length():
    assert usrs.is_valid_email(MIN_LENGTH)


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


def test_long_domain():
    assert not usrs.is_valid_email(LONG_TLD)


#TO BE UNCOMMENTED AFTER ROLES PARAMETER ADDED TO OTHER FUNCTIONS
# TEMP_EMAIL = 'fake_user_email@gmail.com'
# TEMP_ROLE_CODE = 'Author'


# @pytest.fixture(scope='function')
# def temp_user():
#     _id = usrs.create('Billy Bob', 'NYU', TEMP_EMAIL, TEMP_ROLE_CODE)
#     yield _id
#     usrs.delete(_id)


# def test_has_roles(temp_user):
#     user_record = usrs.read_one(temp_user)
#     assert usrs.has_role(user_record, TEMP_ROLE_CODE)


# def test_create_mh_rec(temp_user):
#     person_rec = usrs.read_one(temp_user)
#     mh_rec = usrs.create_mh_rec(person_rec)
#     assert isinstance(mh_rec, dict)
#     for field in usrs.MH_FIELDS:
#         assert field in mh_rec
