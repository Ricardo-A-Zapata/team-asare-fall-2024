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
    for code in mh_roles:
        assert code in rls.MH_ROLES
    for code in rls.MH_ROLES:
        assert code in mh_roles
    

def test_is_valid():
    assert rls.is_valid(rls.TEST_CODE)
    assert not rls.is_valid("INVALID_CODE")


def test_create(temp_role):
    assert temp_role['code'] in rls.ROLES
    assert rls.ROLES[temp_role['code']] == temp_role['role']


def test_create_duplicate():
    rls.create("DUP", "Duplicate Role")
    with pytest.raises(ValueError):
        rls.create("DUP", "Another Duplicate Role")
    assert rls.read_one("DUP") == "Duplicate Role"


def test_read_one(temp_role):
    role = rls.read_one(temp_role['code'])
    assert role == temp_role['role']
    assert rls.read_one("INVALID_CODE") is None


def test_update(temp_role):
    updated_role = "Updated Role"
    result = rls.update(temp_role['code'], updated_role)
    assert result is True
    assert rls.get_roles()[temp_role['code']] == updated_role
    other_roles = {code: name for code, name in rls.get_roles().items() if code != temp_role['code']}
    for code, name in other_roles.items():
        assert name != updated_role  


def test_delete(temp_role):
    result = rls.delete(temp_role['code'])
    assert result is True
    assert temp_role['code'] not in rls.ROLES


def test_delete_nonexistent():
    assert not rls.delete("NONEXISTENT")


def test_list_role_codes():
    role_codes = rls.list_role_codes()
    assert isinstance(role_codes, list)
    assert len(role_codes) > 0
    for code in role_codes:
        assert isinstance(code, str)
        assert code in rls.ROLES


def test_create_edge_cases():
    short_code, short_name = "A", "Short"
    assert rls.create(short_code, short_name)
    assert short_code in rls.get_roles()
    assert rls.get_roles()[short_code] == short_name

    special_code, special_name = "R@#!$", "Special!@#"
    assert rls.create(special_code, special_name)
    assert special_code in rls.get_roles()
    assert rls.get_roles()[special_code] == special_name

    long_code, long_name = "L" * 100, "Long Name" * 20
    assert rls.create(long_code, long_name)
    assert long_code in rls.get_roles()
    assert rls.get_roles()[long_code] == long_name

    empty_name = ""
    assert rls.create("EMPTY", empty_name)
    assert rls.get_roles()["EMPTY"] == empty_name

    whitespace_code, whitespace_name = "   ", "Whitespace Role"
    assert rls.create(whitespace_code.strip(), whitespace_name.strip())

@pytest.fixture(scope='function')
def temp_role():
    temp = {'code':'Temp Role Code', 'role':'Temp Role Value'}
    rls.create(**temp)
    yield temp
    if rls.read_one(temp['code']): rls.delete(temp['code'])