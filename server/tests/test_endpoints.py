from http.client import (
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
)

from unittest.mock import patch

import pytest
import data.text as txt
import data.db_connect as dbc
import data.roles as rls
import server.endpoints as ep
import data.manuscripts as ms


TEST_CLIENT = None

# Define test constants at the top of your test file
TEST_ROLE_CODE = "TR"
TEST_ROLE_NAME = "Test Role"
NE_VALUE = "NONEXISTENT VALUE"

@pytest.fixture(autouse=True)
def setup_test_client():
    """
    Setup a test client before each test.
    This fixture also configures the app for testing.
    """
    global TEST_CLIENT
    ep.app.config['TESTING'] = True
    TEST_CLIENT = ep.app.test_client()
    yield TEST_CLIENT
    ep.app.config['TESTING'] = False


@pytest.fixture(autouse=True)
def setup_test_text_db():
    """
    Set up test text database before each test and clean up after
    """
    dbc.client[dbc.JOURNAL_DB][txt.TEST_COLLECTION].drop()
    yield
    dbc.client[dbc.JOURNAL_DB][txt.TEST_COLLECTION].drop()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_journal_name():
    resp = TEST_CLIENT.get(ep.JOURNAL_NAME_EP)
    resp_json = resp.get_json()
    assert ep.JOURNAL_NAME_RESP in resp_json
    assert isinstance(resp_json[ep.JOURNAL_NAME_RESP], str)


def test_create():
    # Sample User For Test
    test = {
        "name": "test_user",
        "email": "test@user.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "role": "TR",
    }
    resp = TEST_CLIENT.put(ep.USERS_EP, json=test)
    assert resp.status_code == OK
    assert resp.json[ep.USERS_RESP] == 'User added!'

    # Clean up
    TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')


def test_update_users():
    # First create a user to update
    test = {
        "name": "test_name",
        "email": "test@user.com",
        "affiliation": "Test Uni",
    }
    TEST_CLIENT.put(ep.USERS_EP, json=test)

    test_update = {
        'name': "updated_name",
        "email": "test@user.com",
        "affiliation": "University",
    }
    resp = TEST_CLIENT.put(ep.USER_UPDATE_EP, json=test_update)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json['return'] is True
    assert ep.USER_UPDATE_RESP in resp_json

    # Clean up
    TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')


@patch('data.users.read', autospec=True, return_value={
    'ejc369@nyu.edu': {
        'name': 'Eugene Callahan',
        'email': 'ejc369@nyu.edu',
        'affiliation': 'NYU',
        'roles': []
    }
})
def test_read_users(mock_read):
    resp = TEST_CLIENT.get(ep.USER_READ_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.USER_READ_RESP in resp_json
    assert isinstance(resp_json[ep.USER_READ_RESP], dict)
    user_data = resp_json[ep.USER_READ_RESP].get('ejc369@nyu.edu')
    assert user_data is not None
    assert user_data['name'] == 'Eugene Callahan'
    assert user_data['affiliation'] == 'NYU'


def test_delete():
    test = {
        "name": "Random Name",
        "email": "randomNametoTest@hotmail.com",
        "affiliation": "Random Uni",
    }

    TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')

    resp = TEST_CLIENT.put(ep.USERS_EP, json=test)
    assert resp.status_code == OK, "Could not create test user to delete"

    resp = TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')
    assert resp.status_code == OK
    assert resp.json[ep.USER_DELETE_RESP] == 'success'

    resp = TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')
    assert resp.status_code == NOT_FOUND


def test_create_text():
    try:
        resp = TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=ep.TEST_CREATE_TEXT)
        assert resp.status_code == OK
        assert resp.json[ep.TEXT_CREATE_RESP] == 'Text entry created!'
        
        # Verify text was created in test DB
        text = txt.read_one(ep.TEST_CREATE_TEXT["key"], testing=True)
        assert text is not None
        assert text[txt.TITLE] == ep.TEST_CREATE_TEXT["title"]
        assert text[txt.TEXT] == ep.TEST_CREATE_TEXT["text"]
    finally:
        # Clean up
        txt.delete(ep.TEST_CREATE_TEXT["key"], testing=True)


@pytest.fixture()
def test_text():
    """
    Setup a test text entry before each test.
    """
    resp = TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=ep.TEST_CREATE_TEXT)
    if resp.status_code == OK:
        yield resp
    else:
        raise Exception("Could not create test text")
    if txt.read_one(ep.TEST_CREATE_TEXT["key"]):
        txt.delete(ep.TEST_CREATE_TEXT["key"], testing=True)


def test_duplicate_text(test_text):
    # First creation should succeed
    assert test_text.status_code == OK
    
    # Second creation should fail
    resp = TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=ep.TEST_CREATE_TEXT)
    assert resp.status_code == NOT_ACCEPTABLE
        

def test_read_text(test_text):
    assert test_text.status_code == OK
    resp = TEST_CLIENT.get(f'{ep.TEXT_READ_EP}/{ep.TEST_CREATE_TEXT["key"]}')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.TEXT_READ_RESP in resp_json
    assert resp_json[ep.TEXT_READ_RESP]['title'] == ep.TEST_CREATE_TEXT['title']
    assert resp_json[ep.TEXT_READ_RESP]['text'] == ep.TEST_CREATE_TEXT['text']


def test_delete_text(test_text):    
    # Verify text exists in test DB
    text = txt.read_one(ep.TEST_CREATE_TEXT["key"], testing=True)
    assert text is not None
    
    # Delete entry
    resp = TEST_CLIENT.delete(f'{ep.TEXT_DELETE_EP}/{ep.TEST_CREATE_TEXT["key"]}')
    assert resp.status_code == OK
    assert resp.json[ep.TEXT_DELETE_RESP] == 'Text entry deleted!'

    # Verify text was deleted from test DB
    text = txt.read_one(ep.TEST_CREATE_TEXT["key"], testing=True)
    assert not text

def test_delete_nonexistent_text():
    # Test deleting non-existent text
    resp = TEST_CLIENT.delete(f'{ep.TEXT_DELETE_EP}/{NE_VALUE}')
    assert resp.status_code == NOT_FOUND


def test_update_text(test_text):
    updated_text = {i: j for i, j in ep.TEST_CREATE_TEXT.items()}
    updated_text['title'] = "New Title"
    updated_text['text'] = "New Text Content"
    
    resp = TEST_CLIENT.put(ep.TEXT_UPDATE_EP, json=updated_text)
    assert resp.status_code == OK
    assert resp.json[ep.TEXT_UPDATE_RESP] == 'Text entry updated successfully'

    # Verify update in test DB
    text = txt.read_one(updated_text["key"], testing=True)
    assert text is not None
    assert text[txt.TITLE] == updated_text['title']
    assert text[txt.TEXT] == updated_text['text']


def test_update_nonexistent_text():
    nonexistent_text = {
        "key": NE_VALUE,
        "title": "Nonexistent Title",
        "text": "This text doesn't exist."
    }
    resp = TEST_CLIENT.put(ep.TEXT_UPDATE_EP, json=nonexistent_text)
    assert resp.status_code == NOT_ACCEPTABLE


def test_read_roles():
    # Ensure the role does not exist before testing
    rls.delete(TEST_ROLE_CODE, testing=True)

    # Ensure the role exists before testing
    rls.create(TEST_ROLE_CODE, TEST_ROLE_NAME, testing=True)
    
    resp = TEST_CLIENT.get(ep.ROLE_READ_EP)
    assert resp.status_code == OK
    assert ep.ROLE_READ_RESP in resp.json
    assert isinstance(resp.json[ep.ROLE_READ_RESP], dict)
    assert TEST_ROLE_CODE in resp.json[ep.ROLE_READ_RESP]

    # Clean up
    rls.delete(TEST_ROLE_CODE, testing=True)


def test_read_roles_plural():
    """Test the /roles/read endpoint returns roles in correct format"""
    # Create a test role first
    test_role = {
        "code": TEST_ROLE_CODE,
        "role": TEST_ROLE_NAME
    }
    TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)

    try:
        resp = TEST_CLIENT.get('/roles')
        assert resp.status_code == OK
        assert len(resp.json) > 0  # At least one role should exist
        assert TEST_ROLE_CODE in resp.json  # Our test role should be there
    finally:
        # Clean up
        TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/{TEST_ROLE_CODE}')


def test_create_role():
    # Ensure the role does not exist before creating
    rls.delete(TEST_ROLE_CODE, testing=True)

    resp = TEST_CLIENT.post(ep.ROLE_CREATE_EP, json={
        "code": TEST_ROLE_CODE,
        "role": TEST_ROLE_NAME
    })
    assert resp.status_code == OK
    assert resp.json[ep.ROLE_CREATE_RESP] == 'Role created!'

    # Clean up
    TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/{TEST_ROLE_CODE}')


def test_create_duplicate_role():
    test_role = {
        "code": "TR",
        "role": "Test Role"
    }
    # Create first time
    TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)
    
    # Try to create duplicate
    resp = TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)
    assert resp.status_code == NOT_ACCEPTABLE

    # Clean up
    TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/{test_role["code"]}')


def test_read_one_role():
    # Create test role first
    test_role = {
        "code": "TR",
        "role": "Test Role"
    }
    TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)

    resp = TEST_CLIENT.get(f'{ep.ROLE_READ_EP}/TR')
    assert resp.status_code == OK
    assert ep.ROLE_READ_RESP in resp.json
    assert isinstance(resp.json[ep.ROLE_READ_RESP], str)

    # Clean up
    TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/{test_role["code"]}')


def test_update_role():
    # Create test role first
    test_role = {
        "code": "TR",
        "role": "Test Role"
    }
    TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)

    updated_role = {
        "code": "TR",
        "role": "Updated Test Role"
    }
    resp = TEST_CLIENT.put(ep.ROLE_UPDATE_EP, json=updated_role)
    assert resp.status_code == OK
    assert resp.json[ep.ROLE_UPDATE_RESP] == 'Role updated!'

    # Clean up
    TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/{test_role["code"]}')


def test_update_nonexistent_role():
    updated_role = {
        "code": "NE",
        "role": NE_VALUE,
    }
    resp = TEST_CLIENT.put(ep.ROLE_UPDATE_EP, json=updated_role)
    assert resp.status_code == NOT_ACCEPTABLE


def test_delete_role():
    # Create test role first
    test_role = {
        "code": "TR",
        "role": "Test Role"
    }
    # Ensure the role exists
    TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)

    # Test deleting the role
    resp = TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/TR')
    assert resp.status_code == OK
    assert resp.json[ep.ROLE_DELETE_RESP] == 'Role deleted!'


def test_delete_nonexistent_role():
    resp = TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/{NE_VALUE}')
    assert resp.status_code == NOT_FOUND


def test_masthead():
    resp = TEST_CLIENT.get(ep.USER_GET_MASTHEAD)
    resp_json = resp.get_json()
    assert ep.USER_GET_MASTHEAD_RESP in resp_json


def test_read_single_user():
    """
    Test retrieving a single user by email
    """
    # Create test user
    test = {
        "name": "test_user",
        "email": "test@user.com",
        "affiliation": "Test Uni",
    }
    
    try:
        # Create user and verify creation
        resp = TEST_CLIENT.put(ep.USERS_EP, json=test)
        assert resp.status_code == OK
        assert resp.json[ep.USERS_RESP] == 'User added!'
        
        # Test reading the single user
        resp = TEST_CLIENT.get(f'{ep.USER_READ_EP}/{test["email"]}')
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert ep.USER_READ_RESP in resp_json
        assert isinstance(resp_json[ep.USER_READ_RESP], dict)
        assert resp_json[ep.USER_READ_RESP]['name'] == test['name']
        assert resp_json[ep.USER_READ_RESP]['email'] == test['email']

        # Test retrieving non-existent user
        resp = TEST_CLIENT.get(f'{ep.USER_READ_EP}/{NE_VALUE}@email.com')
        assert resp.status_code == NOT_FOUND

    finally:
        # Clean up
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')


def test_read_all_texts():
    """
    Test retrieving all text entries
    """
    test_texts = [
        {
            "key": "test_key1",
            "title": "Test Title 1",
            "text": "This is test text 1."
        },
        {
            "key": "test_key2",
            "title": "Test Title 2",
            "text": "This is test text 2."
        }
    ]
    
    # Create test texts
    for text in test_texts:
        TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=text)
        # Verify creation in test DB
        assert txt.read_one(text["key"], testing=True) is not None
    
    resp = TEST_CLIENT.get(ep.TEXT_READ_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.TEXT_READ_RESP in resp_json
    assert isinstance(resp_json[ep.TEXT_READ_RESP], dict)
    
    texts = resp_json[ep.TEXT_READ_RESP]
    assert "test_key1" in texts
    assert "test_key2" in texts
    assert texts["test_key1"]["title"] == "Test Title 1"
    assert texts["test_key2"]["title"] == "Test Title 2"

    # Clean up
    for text in test_texts:
        txt.delete(text["key"], testing=True)

TEST_MANUSCRIPT = {
    "title": "Test Manuscript",
    "author": "Test Author",
    "author_email": "author@test.com",
    "text": "random ahhh text",
    "abstract": "Test abstract"
}

def test_create_manuscript():
    resp = TEST_CLIENT.put('/manuscript/create', json=TEST_MANUSCRIPT)
    assert resp.status_code == OK
    assert resp.json['manuscript']['title'] == TEST_MANUSCRIPT['title']
    TEST_CLIENT.delete(f"/manuscript/delete/{resp.json['manuscript']['_id']}")

def test_get_all_manuscripts():
    _id = TEST_CLIENT.put('/manuscript/create', json=TEST_MANUSCRIPT).json['manuscript']['_id']
    resp = TEST_CLIENT.get('/manuscripts')
    assert resp.status_code == OK
    assert resp.json['count'] >= 1
    assert TEST_MANUSCRIPT['title'] in [m['title'] for m in resp.json['manuscripts'].values()]
    TEST_CLIENT.delete(f'/manuscript/delete/{_id}')
    
def test_create_invalid_manuscript():
    # same data as above but no title, so it is invalid
    invalid_data = {**TEST_MANUSCRIPT, "title": ""}
    resp = TEST_CLIENT.put('/manuscript/create', json=invalid_data)
    assert resp.status_code == NOT_ACCEPTABLE
    assert "Title must be between" in resp.json['message']
    
    # long abstract
    invalid_data = {**TEST_MANUSCRIPT,
                    "abstract": "a" * (ms.MAX_ABSTRACT_LENGTH + 1)}
    resp = TEST_CLIENT.put('/manuscript/create', json=invalid_data)
    assert resp.status_code == NOT_ACCEPTABLE
    msg = "Abstract must be between 0 and 5000 characters"
    assert msg in resp.json['message']

def test_create_manuscript_no_title():
    # Missing 'title' completely, not just empty
    invalid_data = {
        "author": "Test Author",
        "author_email": "author@test.com",
        "text": "Valid text content",
        "abstract": "Valid abstract"
    }
    resp = TEST_CLIENT.put('/manuscript/create', json=invalid_data)
    assert resp.status_code == NOT_ACCEPTABLE
    assert "'title'" in resp.json['message']

TEST_MANUSCRIPT_ID = "60d21b4667d0d8992e610c85"

def test_delete_manuscript_success():
    """Test successful deletion of a manuscript."""
    with patch("data.manuscripts.get_manuscript") as mock_get, \
         patch("data.manuscripts.delete_manuscript") as mock_delete:

        mock_get.return_value = {"_id": TEST_MANUSCRIPT_ID, "state": ms.STATE_SUBMITTED}
        mock_delete.return_value = {"_id": TEST_MANUSCRIPT_ID, "message": "Deleted"}

        resp = TEST_CLIENT.delete(f"/manuscript/delete/{TEST_MANUSCRIPT_ID}")
        assert resp.status_code == OK
        assert "Manuscript deleted successfully" in resp.json["message"]


def test_delete_manuscript_not_found():
    """Test deletion attempt when the manuscript is not found."""
    with patch("data.manuscripts.get_manuscript") as mock_get:
        mock_get.return_value = None

        resp = TEST_CLIENT.delete(f"/manuscript/delete/{TEST_MANUSCRIPT_ID}")
        assert resp.status_code == NOT_FOUND

        # Check for error message in response
        resp_json = resp.get_json()
        assert resp_json is not None, "Response JSON is None"
        assert "error" in resp_json or "message" in resp_json, f"Unexpected response: {resp_json}"
        assert "not found" in resp_json.get("error", resp_json.get("message", ""))


def test_delete_manuscript_published():
    """Test deletion attempt of a published manuscript, which should be forbidden."""
    with patch("data.manuscripts.get_manuscript") as mock_get:
        mock_get.return_value = {"_id": TEST_MANUSCRIPT_ID, "state": ms.STATE_PUBLISHED}

        resp = TEST_CLIENT.delete(f"/manuscript/delete/{TEST_MANUSCRIPT_ID}")
        assert resp.status_code == FORBIDDEN
        assert "Cannot delete a published manuscript" in resp.json["error"]

def test_user_count():
    resp = TEST_CLIENT.get(ep.USER_COUNT_EP)
    assert resp.status_code == OK
    resp = resp.get_json()
    assert ep.USER_COUNT_RESP in resp
    assert resp[ep.USER_COUNT_RESP] >= 0

def test_login():
    test = {
        "name": "test_user",
        "email": "test@user.com",
        "password": "pass",
        "affiliation": "Test Uni",
    }
    ret = TEST_CLIENT.put(ep.USERS_EP, json=test)
    assert ret.status_code == OK
    # Correct Login
    ret = TEST_CLIENT.post(ep.USER_LOGIN_EP, 
                          json={"email": test['email'], "password": test['password']})
    assert ret.status_code == OK
    assert ret.get_json()[ep.USER_LOGIN_RESP] == "Success"
    # Incorrect Login - Email
    ret = TEST_CLIENT.post(
        ep.USER_LOGIN_EP,
        json={"email": 'WRONG@EMAIL.COM', "password": 'TEST_PASSWORD'}
    )
    assert ret.status_code == NOT_ACCEPTABLE
    # Incorrect Login - Password
    ret = TEST_CLIENT.post(
        ep.USER_LOGIN_EP,
        json={"email": test['email'], "password": test['password']+"wrong"}
    )
    assert ret.status_code == NOT_ACCEPTABLE
    TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')

def test_change_password():
    test = {
        "name": "test_user",
        "email": "test@user.com",
        "password": "pass",
        "affiliation": "Test Uni",
    }
    ret = TEST_CLIENT.put(ep.USERS_EP, json=test)
    assert ret.status_code == OK
    ret = TEST_CLIENT.post(
        ep.PASSWORD_UPDATE_EP, 
        json={"email": 'WRONG@EMAIL.COM', "password": 'TEST_PASSWORD'}
    )
    assert ret.status_code == NOT_ACCEPTABLE
    ret = TEST_CLIENT.post(
        ep.PASSWORD_UPDATE_EP,
        json={"password": 'TEST_PASSWORD'}
    )
    assert ret.status_code == NOT_ACCEPTABLE
    ret = TEST_CLIENT.post(
        ep.PASSWORD_UPDATE_EP,
        json={"email": 'test@user.com', "password": 'TEST_PASSWORD'}
    )
    assert ret.status_code == OK
    ret = TEST_CLIENT.post(
        ep.USER_LOGIN_EP,
        json={"email": test['email'], "password": test['password']}
    )
    assert ret.status_code == NOT_ACCEPTABLE
    ret = TEST_CLIENT.post(
        ep.USER_LOGIN_EP,
        json={"email": test['email'], "password": 'TEST_PASSWORD'}
    )
    assert ret.status_code == OK
    TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')

def test_assign_referee():
    """Test if an editor can assign a referee to a manuscript."""
    # First create a manuscript
    manuscript_resp = TEST_CLIENT.put('/manuscript/create', json=TEST_MANUSCRIPT)
    assert manuscript_resp.status_code == OK
    manuscript_id = manuscript_resp.json['manuscript']['_id']

    # Create a referee user
    referee = {
        "name": "Test Referee",
        "email": "referee@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roles": ["RE"]
    }
    referee_resp = TEST_CLIENT.put(ep.USERS_EP, json=referee)
    assert referee_resp.status_code == OK
    # Patch in roleCodes for backend compatibility
    TEST_CLIENT.put(ep.USER_UPDATE_EP, json={
        "name": referee["name"],
        "email": referee["email"],
        "affiliation": referee["affiliation"],
        "roleCodes": ["RE"]
    })

    # Create an editor user
    editor = {
        "name": "Test Editor",
        "email": "editor@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roles": ["ED"]
    }
    editor_resp = TEST_CLIENT.put(ep.USERS_EP, json=editor)
    assert editor_resp.status_code == OK
    # Patch in roleCodes for backend compatibility
    TEST_CLIENT.put(ep.USER_UPDATE_EP, json={
        "name": editor["name"],
        "email": editor["email"],
        "affiliation": editor["affiliation"],
        "roleCodes": ["ED"]
    })

    try:
        # Test editor assigning referee
        resp = TEST_CLIENT.put(
            f'/manuscript/referee/{manuscript_id}',
            json={"referee_email": referee["email"]},
            headers={"X-User-Email": editor["email"]}
        )
        assert resp.status_code == OK
        assert resp.json['Manuscript Referee']['referee_email'] == referee["email"]

    finally:
        # Clean up
        TEST_CLIENT.delete(f'/manuscript/delete/{manuscript_id}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{referee["email"]}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{editor["email"]}')

def test_referee_accept_decision():
    """Test if a referee can accept a manuscript."""
    # First create a manuscript
    manuscript_resp = TEST_CLIENT.put('/manuscript/create', json=TEST_MANUSCRIPT)
    assert manuscript_resp.status_code == OK
    manuscript_id = manuscript_resp.json['manuscript']['_id']

    # Create a referee user
    referee = {
        "name": "Test Referee",
        "email": "referee@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roles": ["RE"]
    }
    referee_resp = TEST_CLIENT.put(ep.USERS_EP, json=referee)
    assert referee_resp.status_code == OK
    # Patch in roleCodes for backend compatibility
    TEST_CLIENT.put(ep.USER_UPDATE_EP, json={
        "name": referee["name"],
        "email": referee["email"],
        "affiliation": referee["affiliation"],
        "roleCodes": ["RE"]
    })

    # Create an editor user
    editor = {
        "name": "Test Editor",
        "email": "editor@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roles": ["ED"]
    }
    editor_resp = TEST_CLIENT.put(ep.USERS_EP, json=editor)
    assert editor_resp.status_code == OK
    # Patch in roleCodes for backend compatibility
    TEST_CLIENT.put(ep.USER_UPDATE_EP, json={
        "name": editor["name"],
        "email": editor["email"],
        "affiliation": editor["affiliation"],
        "roleCodes": ["ED"]
    })

    try:
        # First assign the referee (as editor)
        assign_resp = TEST_CLIENT.put(
            f'/manuscript/referee/{manuscript_id}',
            json={"referee_email": referee["email"]},
            headers={"X-User-Email": editor["email"]}
        )
        assert assign_resp.status_code == OK

        # Test referee accepting manuscript
        accept_resp = TEST_CLIENT.put(
            f'/manuscript/state/{manuscript_id}',
            json={"state": "ACCEPTED"},
            headers={"X-User-Email": referee["email"]}
        )
        assert accept_resp.status_code == OK
        assert accept_resp.json['Manuscript State']['state'] == "ACCEPTED"

    finally:
        # Clean up
        TEST_CLIENT.delete(f'/manuscript/delete/{manuscript_id}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{referee["email"]}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{editor["email"]}')

def test_referee_reject_decision():
    """Test if a referee can reject a manuscript."""
    # First create a manuscript
    manuscript_resp = TEST_CLIENT.put('/manuscript/create', json=TEST_MANUSCRIPT)
    assert manuscript_resp.status_code == OK
    manuscript_id = manuscript_resp.json['manuscript']['_id']

    # Create a referee user
    referee = {
        "name": "Test Referee",
        "email": "referee@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roles": ["RE"]
    }
    referee_resp = TEST_CLIENT.put(ep.USERS_EP, json=referee)
    assert referee_resp.status_code == OK
    # Patch in roleCodes for backend compatibility
    TEST_CLIENT.put(ep.USER_UPDATE_EP, json={
        "name": referee["name"],
        "email": referee["email"],
        "affiliation": referee["affiliation"],
        "roleCodes": ["RE"]
    })

    # Create an editor user
    editor = {
        "name": "Test Editor",
        "email": "editor@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roles": ["ED"]
    }
    editor_resp = TEST_CLIENT.put(ep.USERS_EP, json=editor)
    assert editor_resp.status_code == OK
    # Patch in roleCodes for backend compatibility
    TEST_CLIENT.put(ep.USER_UPDATE_EP, json={
        "name": editor["name"],
        "email": editor["email"],
        "affiliation": editor["affiliation"],
        "roleCodes": ["ED"]
    })

    try:
        # First assign the referee (as editor)
        assign_resp = TEST_CLIENT.put(
            f'/manuscript/referee/{manuscript_id}',
            json={"referee_email": referee["email"]},
            headers={"X-User-Email": editor["email"]}
        )
        assert assign_resp.status_code == OK

        # Test referee rejecting manuscript
        reject_resp = TEST_CLIENT.put(
            f'/manuscript/state/{manuscript_id}',
            json={"state": "REJECTED"},
            headers={"X-User-Email": referee["email"]}
        )
        assert reject_resp.status_code == OK
        assert reject_resp.json['Manuscript State']['state'] == "REJECTED"

    finally:
        # Clean up
        TEST_CLIENT.delete(f'/manuscript/delete/{manuscript_id}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{referee["email"]}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{editor["email"]}')

def test_remove_referee():
    """Test removing a referee from a manuscript."""
    # First create a manuscript
    manuscript_resp = TEST_CLIENT.put('/manuscript/create', json=TEST_MANUSCRIPT)
    assert manuscript_resp.status_code == OK
    manuscript_id = manuscript_resp.json['manuscript']['_id']

    # Create a referee user
    referee = {
        "name": "Test Referee",
        "email": "referee@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roleCodes": ["RE"]
    }
    TEST_CLIENT.put(ep.USERS_EP, json=referee)

    # Create an editor user
    editor = {
        "name": "Test Editor",
        "email": "editor@test.com",
        "password": "pass",
        "affiliation": "Test Uni",
        "roleCodes": ["ED"]
    }
    TEST_CLIENT.put(ep.USERS_EP, json=editor)

    try:
        # Assign referee (as editor)
        TEST_CLIENT.put(
            f'/manuscript/referee/{manuscript_id}',
            json={"referee_email": referee["email"]},
            headers={"X-User-Email": editor["email"]}
        )

        # Remove referee
        resp = TEST_CLIENT.delete(
            f'/manuscript/referee/{manuscript_id}?referee_email={referee["email"]}',
            headers={"X-User-Email": editor["email"]}
        )
        assert resp.status_code == OK
        assert "Referee removed" in resp.json["message"]

    finally:
        # Clean up
        TEST_CLIENT.delete(f'/manuscript/delete/{manuscript_id}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{referee["email"]}')
        TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{editor["email"]}')

    