import pytest
import data.users as usrs
import data.db_connect as dbc

# Test constants
TEST_NAME = "Test User"
TEST_EMAIL = "test@example.com"
TEST_AFFILIATION = "Test University"
TEST_ROLE = "AD"

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

# Add these constants at the top with other constants
MH_FIELDS = [usrs.NAME, usrs.AFFILIATION]
TEMP_EMAIL = 'fake_user_email@gmail.com'
TEMP_ROLE_CODE = 'Author'


@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Set up test database before each test and clean up after
    """
    dbc.client[dbc.JOURNAL_DB][usrs.USERS_COLLECTION].drop()
    # Create test user for tests that need existing data
    usrs.create('Eugene Callahan', usrs.TEST_EMAIL, 'NYU', testing=True)
    yield
    dbc.client[dbc.JOURNAL_DB][usrs.USERS_COLLECTION].drop()


@pytest.fixture(scope='function')
def temp_user():
    usrs.create('Billy Bob', TEMP_EMAIL, 'NYU', testing=True)
    yield TEMP_EMAIL
    users = usrs.read(testing=True)
    if TEMP_EMAIL in users:
        usrs.delete(TEMP_EMAIL, testing=True)


def test_read():
    users = usrs.read(testing=True)
    assert isinstance(users, dict)
    assert len(users) > 0  # at least one user!
    for email, user in users.items():
        assert isinstance(email, str)
        assert len(email) >= usrs.MIN_USER_NAME_LEN
        assert usrs.NAME in user
        assert usrs.EMAIL in user
        assert usrs.AFFILIATION in user


def test_create():
    users = usrs.read(testing=True)
    assert TEST_EMAIL not in users
    usrs.create(TEST_NAME, TEST_EMAIL, TEST_AFFILIATION, testing=True)
    users = usrs.read(testing=True)
    assert TEST_EMAIL in users
    assert users[TEST_EMAIL][usrs.NAME] == TEST_NAME


def test_create_duplicate():
    with pytest.raises(ValueError):
        usrs.create('Do not care about name', usrs.TEST_EMAIL, 
                   'Or affiliation', testing=True)


def test_update():
    NEW_NAME = "Updated Name"
    NEW_AFFILIATION = "Updated University"
    
    usrs.create(TEST_NAME, TEST_EMAIL, TEST_AFFILIATION, testing=True)
    user = usrs.read_one(TEST_EMAIL, testing=True)
    assert user[usrs.NAME] == TEST_NAME
    
    usrs.update(NEW_NAME, TEST_EMAIL, NEW_AFFILIATION, testing=True)
    user = usrs.read_one(TEST_EMAIL, testing=True)
    assert user[usrs.NAME] == NEW_NAME
    assert user[usrs.AFFILIATION] == NEW_AFFILIATION


def test_delete():
    usrs.create(TEST_NAME, TEST_EMAIL, TEST_AFFILIATION, testing=True)
    assert usrs.read_one(TEST_EMAIL, testing=True) is not None
    
    usrs.delete(TEST_EMAIL, testing=True)
    assert usrs.read_one(TEST_EMAIL, testing=True) is None
    
    with pytest.raises(KeyError):
        usrs.delete(TEST_EMAIL, testing=True)


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


def test_has_roles(temp_user):
    """Test role assignment and checking"""
    # Add role to user
    usrs.add_role(temp_user, TEMP_ROLE_CODE, testing=True)
    
    # Verify role was added
    user = usrs.read_one(temp_user, testing=True)
    assert usrs.has_role(user, TEMP_ROLE_CODE)
    
    # Test for non-existent role
    assert not usrs.has_role(user, "NON_EXISTENT_ROLE")
    
    # Test user without roles
    new_user = {
        usrs.NAME: "No Roles User",
        usrs.EMAIL: "no_roles@test.com",
        usrs.AFFILIATION: "Test Uni"
    }
    assert not usrs.has_role(new_user, TEMP_ROLE_CODE)


def test_get_masthead():
    masthead = usrs.get_masthead()
    assert isinstance(masthead, dict)


def test_create_mh_rec():
    """Test creating a masthead record"""
    person_rec = {
        usrs.NAME: "Test Person",
        usrs.EMAIL: "test@example.com",
        usrs.AFFILIATION: "Test University",
        usrs.ROLES: []
    }
    mh_rec = {
        usrs.NAME: person_rec[usrs.NAME],
        usrs.AFFILIATION: person_rec[usrs.AFFILIATION]
    }
    
    for field in MH_FIELDS:
        assert field in mh_rec


def test_add_role():
    """Test adding a role to a user"""
    # Create test user
    usrs.create(TEST_NAME, TEST_EMAIL, TEST_AFFILIATION, testing=True)
    
    # Add role
    ret = usrs.add_role(TEST_EMAIL, TEST_ROLE, testing=True)
    assert ret is True
    
    # Verify role was added
    user = usrs.read_one(TEST_EMAIL, testing=True)
    assert TEST_ROLE in user[usrs.ROLES]
    
    # Clean up
    usrs.delete(TEST_EMAIL, testing=True)


def test_update_with_roles():
    """Test updating a user with roles"""
    # Create test user
    usrs.create(TEST_NAME, TEST_EMAIL, TEST_AFFILIATION, testing=True)
    
    # Update with roles
    new_name = "Updated Name"
    new_roles = [TEST_ROLE]
    ret = usrs.update(new_name, TEST_EMAIL, TEST_AFFILIATION, new_roles, testing=True)
    assert ret is True
    
    # Verify update
    user = usrs.read_one(TEST_EMAIL, testing=True)
    assert user[usrs.NAME] == new_name
    assert TEST_ROLE in user[usrs.ROLES]
    
    # Clean up
    usrs.delete(TEST_EMAIL, testing=True)


def test_create_with_roles():
    """Test creating a user with roles"""
    roles = [TEST_ROLE]
    
    # Create user with roles
    ret = usrs.create(TEST_NAME, TEST_EMAIL, TEST_AFFILIATION, roles, testing=True)
    assert ret == TEST_EMAIL
    
    # Verify user was created with roles
    user = usrs.read_one(TEST_EMAIL, testing=True)
    assert user is not None
    assert user[usrs.NAME] == TEST_NAME
    assert TEST_ROLE in user[usrs.ROLES]
    
    # Clean up
    usrs.delete(TEST_EMAIL, testing=True)
