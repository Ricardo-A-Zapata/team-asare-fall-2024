import pytest
import data.roles as rls

TEST_ROLE_CODE = "TR"
TEST_ROLE_NAME = "Test Role"

def test_get_roles():
    roles = rls.get_roles()
    assert isinstance(roles, dict)
    assert len(roles) > 0
    for code, role in roles.items():
        assert isinstance(code, str)
        assert isinstance(role, str)


def test_get_masthead_roles():
    mh_roles = rls.get_masthead_roles()
    assert isinstance(mh_roles, dict)
    

def test_is_valid():
    assert rls.is_valid(rls.TEST_CODE)
    assert not rls.is_valid("INVALID_CODE")


def test_create():
    result = rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME)
    assert result is True
    assert TEST_ROLE_CODE in rls.ROLES
    assert rls.ROLES[TEST_ROLE_CODE] == TEST_ROLE_NAME


def test_create_duplicate():
    rls.create("DUP", "Duplicate Role")
    with pytest.raises(ValueError):
        rls.create("DUP", "Another Duplicate Role")


def test_read_one():
    role = rls.read_one(TEST_ROLE_CODE)
    assert role == TEST_ROLE_NAME
    assert rls.read_one("INVALID_CODE") is None


def test_update():
    updated_role = "Updateed Test Role"
    result = rls.update(TEST_ROLE_CODE, updated_role)
    assert result is True
    assert rls.ROLES[TEST_ROLE_CODE] == updated_role


def test_delete():
    result = rls.delete(TEST_ROLE_CODE)
    assert result is True
    assert TEST_ROLE_CODE not in rls.ROLES


def test_delete_nonexistent():
    assert not rls.delete("NONEXISTENT")


def test_list_role_codes():
    role_codes = rls.list_role_codes()
    assert isinstance(role_codes, list)
    assert len(role_codes) > 0
    for code in role_codes:
        assert isinstance(code, str)
        assert code in rls.ROLES
