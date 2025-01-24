import pytest
import data.roles as rls
import data.users as usr
import data.db_connect as dbc

# Constants for testing
TEST_ROLE_CODE = "TR"  # Unique role code for tests
TEST_ROLE_NAME = "Test Role"
ROLES_COLLECTION = 'roles'

@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Fixture to reset the roles collection for testing, ensuring a clean slate.
    """
    db = dbc.client[dbc.JOURNAL_DB]
    db[ROLES_COLLECTION].drop()  # Drop all roles, including seeds
    yield
    db[ROLES_COLLECTION].drop()  # Clean up after tests

def test_create():
    assert rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    assert rls.read_one(TEST_ROLE_CODE, testing=True) == TEST_ROLE_NAME

def test_create_duplicate():
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    with pytest.raises(ValueError):
        rls.create(TEST_ROLE_CODE, "Another Role Name", testing=True)

def test_read_one():
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    role = rls.read_one(TEST_ROLE_CODE, testing=True)
    assert role == TEST_ROLE_NAME
    assert rls.read_one("INVALID_CODE", testing=True) is None

def test_update():
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    updated_role = "Updated Role Name"
    assert rls.update(TEST_ROLE_CODE, updated_role, testing=True)
    assert rls.read_one(TEST_ROLE_CODE, testing=True) == updated_role

def test_delete():
    assert rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    assert rls.delete(TEST_ROLE_CODE, testing=True)
    assert not rls.is_valid(TEST_ROLE_CODE, testing=True)

def test_read_all_roles():
    assert rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    roles = rls.get_roles(testing=True)
    assert isinstance(roles, dict)
    assert TEST_ROLE_CODE in roles
    assert roles[TEST_ROLE_CODE] == TEST_ROLE_NAME