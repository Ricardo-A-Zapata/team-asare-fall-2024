import pytest
import data.roles as rls
import data.db_connect as dbc

# Constants for testing
TEST_ROLE_CODE = "TR"
TEST_ROLE_NAME = "Test Role"
ROLES_COLLECTION = 'roles'

@pytest.fixture(autouse=True)
def setup_test_db():
    dbc.client[dbc.JOURNAL_DB][ROLES_COLLECTION].drop()
    yield
    # clean up after tests
    dbc.client[dbc.JOURNAL_DB][ROLES_COLLECTION].drop()

@pytest.fixture(scope='function')
def temp_role():
    """
    Fixture to create a temporary role for testing.
    """
    temp = {'code': 'TempRoleCode', 'role': 'Temp Role Name'}
    rls.create(temp['code'], temp['role'])
    yield temp
    rls.delete(temp['code'])

def test_get_roles():
    """
    Test retrieving all roles from MongoDB.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    roles = rls.get_roles()
    assert isinstance(roles, dict)
    assert TEST_ROLE_CODE in roles
    assert roles[TEST_ROLE_CODE] == TEST_ROLE_NAME

def test_get_masthead_roles():
    """
    Test retrieving masthead roles.
    """
    rls.create("AU", "Author")
    rls.create("ED", "Editor")
    masthead_roles = rls.get_masthead_roles()
    assert "AU" in masthead_roles
    assert "ED" in masthead_roles
    assert masthead_roles["AU"] == "Author"
    assert masthead_roles["ED"] == "Editor"

def test_is_valid():
    """
    Test validating a role code.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    assert rls.is_valid(TEST_ROLE_CODE)
    assert not rls.is_valid("INVALID_CODE")

def test_create():
    """
    Test creating a new role.
    """
    assert rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    assert rls.read_one(TEST_ROLE_CODE) == TEST_ROLE_NAME

def test_create_duplicate():
    """
    Test creating a duplicate role, which should raise an error.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    with pytest.raises(ValueError):
        rls.create(TEST_ROLE_CODE, "Another Role Name")

def test_read_one():
    """
    Test reading a single role by its code.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    role = rls.read_one(TEST_ROLE_CODE)
    assert role == TEST_ROLE_NAME
    assert rls.read_one("INVALID_CODE") is None

def test_update():
    """
    Test updating an existing role.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    updated_role = "Updated Role Name"
    assert rls.update(TEST_ROLE_CODE, updated_role)
    assert rls.read_one(TEST_ROLE_CODE) == updated_role

def test_delete():
    """
    Test deleting a role.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    assert rls.delete(TEST_ROLE_CODE)
    assert not rls.is_valid(TEST_ROLE_CODE)

def test_delete_nonexistent():
    """
    Test deleting a non-existent role, which should return False.
    """
    assert not rls.delete("NONEXISTENT_CODE")

def test_list_role_codes():
    """
    Test retrieving all role codes from MongoDB.
    """
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    role_codes = rls.list_role_codes()
    assert isinstance(role_codes, list)
    assert TEST_ROLE_CODE in role_codes

def test_create_edge_cases():
    """
    Test creating roles with edge-case names and codes.
    """
    short_code, short_name = "A", "Short"
    assert rls.create(short_code, short_name)
    assert rls.read_one(short_code) == short_name

    special_code, special_name = "R@#!$", "Special!@#"
    assert rls.create(special_code, special_name)
    assert rls.read_one(special_code) == special_name

    long_code, long_name = "L" * 100, "Long Name" * 20
    assert rls.create(long_code, long_name)
    assert rls.read_one(long_code) == long_name