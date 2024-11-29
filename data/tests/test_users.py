import pytest
import data.users as usrs
import data.db_connect as dbc
from data.users import NAME, ROLES

# Test constants
ADD_EMAIL = 'joe@nyu.edu'
ADD_AFFILIATION = "NYU"
VALID_ROLE = "AD"
INVALID_ROLE = "InvalidRole"
BEFORE_NAME = 'before name'
AFTER_NAME = 'after name'
UPDATE_EMAIL = 'update@test.com'

@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Set up test database before each test and clean up after
    """
    # Setup
    dbc.client[dbc.JOURNAL_DB][usrs.TEST_COLLECTION].drop()
    # Create test user
    usrs.create('Eugene Callahan', usrs.TEST_EMAIL, 'NYU', testing=True)
    
    yield
    
    # Teardown
    dbc.client[dbc.JOURNAL_DB][usrs.TEST_COLLECTION].drop()


def test_read():
    users = usrs.read(testing=True)
    assert isinstance(users, dict)
    assert len(users) > 0  # at least one user!
    # keys are user email
    for email, user in users.items():
        assert isinstance(email, str)
        assert len(email) >= usrs.MIN_USER_NAME_LEN
        assert usrs.NAME in user
        assert usrs.EMAIL in user
        assert usrs.AFFILIATION in user


def test_create():
    users = usrs.read(testing=True)
    assert ADD_EMAIL not in users, "User should not already exist before creation"
    usrs.create(NAME, ADD_EMAIL, ADD_AFFILIATION, testing=True)
    users = usrs.read(testing=True)
    assert ADD_EMAIL in users, "User should exist after creation"


def test_update():
    usrs.create(BEFORE_NAME, UPDATE_EMAIL, 'NYU', testing=True)
    users = usrs.read(testing=True)
    assert UPDATE_EMAIL in users
    assert BEFORE_NAME == users[UPDATE_EMAIL][usrs.NAME]
    
    # Update the user and get fresh data
    usrs.update(AFTER_NAME, UPDATE_EMAIL, 'University', testing=True)
    users = usrs.read(testing=True)  # Re-read the users to get updated data
    
    assert AFTER_NAME == users[UPDATE_EMAIL][usrs.NAME]


def test_delete():
    # First create a user
    usrs.create("John Doe", ADD_EMAIL, "NYU", testing=True)
    users = usrs.read(testing=True)
    assert ADD_EMAIL in users, "User should exist after creation"
    
    # Then delete the user
    usrs.delete(ADD_EMAIL, testing=True)
    users = usrs.read(testing=True)
    assert ADD_EMAIL not in users, "User should not exist after deletion"


def test_create_duplicate():
    with pytest.raises(ValueError):
        usrs.create('Do not care about name', usrs.TEST_EMAIL, 'Or affiliation', testing=True)


# Email validation test constants
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


# Role testing constants
TEMP_EMAIL = 'fake_user_email@gmail.com'
TEMP_ROLE_CODE = 'Author'


@pytest.fixture(scope='function')
def temp_user():
    usrs.create('Billy Bob', TEMP_EMAIL, 'NYU', testing=True)
    yield TEMP_EMAIL
    users = usrs.read(testing=True)
    if TEMP_EMAIL in users:
        usrs.delete(TEMP_EMAIL, testing=True)


@pytest.mark.skip(reason="AWAITING ROLES PARAMETER ADDED TO OTHER FUNCTIONS")
def test_has_roles(temp_user):
    user_record = usrs.read_one(temp_user, testing=True)
    assert usrs.has_role(user_record, TEMP_ROLE_CODE)


@pytest.mark.skip(reason="AWAITING ROLES PARAMETER ADDED TO OTHER FUNCTIONS")
def test_create_mh_rec(temp_user):
    person_rec = usrs.read_one(temp_user, testing=True)
    mh_rec = usrs.create_mh_rec(person_rec)
    assert isinstance(mh_rec, dict)
    for field in usrs.MH_FIELDS:
        assert field in mh_rec
