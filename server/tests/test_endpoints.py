from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

import server.endpoints as ep



TEST_CLIENT = ep.app.test_client()

TEST_CREATE_TEXT = {
        "key": "test_key",
        "title": "Test Title",
        "text": "This is a test text."
    }
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
        "affiliation": "Test Uni",
        "role": ep.rls.TEST_CODE,
    }
    resp = TEST_CLIENT.put(ep.USERS_EP, json=test)
    assert resp.status_code == OK
    assert resp.json[ep.USERS_RESP] == 'User added!'

def test_update_users():
    test_update = {'name': "test_name",
	"email": "test@user.com",
	"affiliation": "University",
    }
    resp = TEST_CLIENT.put(ep.USER_UPDATE_EP, json = test_update)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json['return'] == True
    assert ep.USER_UPDATE_RESP in resp_json

def test_read_users():
    resp = TEST_CLIENT.get(ep.USER_READ_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.USER_READ_RESP in resp_json
    assert isinstance(resp_json[ep.USER_READ_RESP], dict)
    # Optionally, verify that the test user is in the response
    assert ep.usr.TEST_EMAIL in resp_json[ep.USER_READ_RESP]


def test_delete():
    # Will try to delete the test user, then will add that user back in
    test = {
    "name": "randomNametoTest",
    "email": "randomNametoTest@hotmail.com",
    "affiliation": "Random Uni to Test",
    }
    resp = TEST_CLIENT.put(ep.USERS_EP, json=test)
    if resp.status_code != OK:
        raise Exception("Could not create test user to delete")
    # test deletion for existing user
    resp = TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')
    assert resp.status_code == OK
    assert resp.json != None, resp.json[ep.USER_DELETE_RESP] == 'Success'

    # test deletion for nonexistent user after it was deleted
    resp = TEST_CLIENT.delete(f'{ep.USER_DELETE_EP}/{test["email"]}')
    assert resp.status_code == NOT_FOUND

def test_create_text():
    resp = TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=TEST_CREATE_TEXT)
    assert resp.status_code == OK
    assert resp.json[ep.TEXT_CREATE_RESP] == 'Text entry created!'


def test_duplicate_text():
    # Makes sure that we can't create duplicate text
    resp = TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=TEST_CREATE_TEXT)
    assert resp.status_code == NOT_ACCEPTABLE


TEXT_READ_EP = '/text/read'
TEXT_READ_RESP = 'Content'


def test_read_text():
    test_text = {
        "key": "read_test_key",
        "title": "Read Test Title",
        "text": "This is a test text for reading."
        }
    TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=test_text)
    resp = TEST_CLIENT.get(f'{ep.TEXT_READ_EP}/{test_text["key"]}')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.TEXT_READ_RESP in resp_json
    assert resp_json[ep.TEXT_READ_RESP]['title'] == test_text['title']
    assert resp_json[ep.TEXT_READ_RESP]['text'] == test_text['text']


def test_delete_text():
    # create text entry
    test_text = {
        "key": "delete_test_key",
        "title": "Delete Test Title",
        "text": "testing testing testing."
    }
    TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=test_text)
    # delete entry
    resp = TEST_CLIENT.delete(f'{ep.TEXT_DELETE_EP}/{test_text["key"]}')
    assert resp.status_code == OK
    assert resp.json[ep.TEXT_DELETE_RESP] == 'Text entry deleted!'

    resp = TEST_CLIENT.get(f'{ep.TEXT_READ_EP}/nonexistent_key')
    assert resp.status_code == NOT_FOUND


def test_update_text():
    test_text = {
        "key": "update_test_key",
        "title": "Update Test Title",
        "text": "This is a test text for updating."
    }
    TEST_CLIENT.post(ep.TEXT_CREATE_EP, json=test_text)

    updated_text = {
        "key": "update_test_key",
        "title": "Updated Title",
        "text": "This text has been updated."
    }
    resp = TEST_CLIENT.put(ep.TEXT_UPDATE_EP, json=updated_text)
    assert resp.status_code == OK
    assert resp.json[ep.TEXT_UPDATE_RESP] == 'Text entry updated successfully'

    resp = TEST_CLIENT.get(f'{ep.TEXT_READ_EP}/{updated_text["key"]}')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json[ep.TEXT_READ_RESP]['title'] == updated_text['title']
    assert resp_json[ep.TEXT_READ_RESP]['text'] == updated_text['text']

def test_update_nonexistent_text():
    nonexistent_text = {
        "key":"nonexistent_key",
        "title":"Nonexistent Title",
        "text":"This text doesn't exist."
    }
    resp = TEST_CLIENT.put(ep.TEXT_UPDATE_EP, json=nonexistent_text)
    assert resp.status_code == NOT_ACCEPTABLE

def test_read_all_roles():
    resp = TEST_CLIENT.get(ep.ROLE_READ_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.ROLE_READ_RESP in resp_json
    assert isinstance(resp_json[ep.ROLE_READ_RESP], dict)
    # Optionally, verify that the test role is in the response
    assert ep.rls.TEST_CODE in resp_json[ep.ROLE_READ_RESP]

def test_create_role():
    test_role = {
        "code": "TR",
        "role": "Test Role"
    }
    resp = TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)
    assert resp.status_code == OK
    assert resp.json[ep.ROLE_CREATE_RESP] == 'Role created!'

def test_create_duplicate_role():
    test_role = {
        "code": "TR",
        "role": "Test Role"
    }
    resp = TEST_CLIENT.post(ep.ROLE_CREATE_EP, json=test_role)
    assert resp.status_code == NOT_ACCEPTABLE

def test_read_roles():
    resp = TEST_CLIENT.get(ep.ROLE_READ_EP)
    assert resp.status_code == OK
    assert ep.ROLE_READ_RESP in resp.json
    assert isinstance(resp.json[ep.ROLE_READ_RESP], dict)

def test_read_one_role():
    resp = TEST_CLIENT.get(f'{ep.ROLE_READ_EP}/TR')
    assert resp.status_code == OK
    assert ep.ROLE_READ_RESP in resp.json
    assert isinstance(resp.json[ep.ROLE_READ_RESP], str)

def test_update_role():
    updated_role = {
        "code": "TR",
        "role": "Updated Test Role"
    }
    resp = TEST_CLIENT.put(ep.ROLE_UPDATE_EP, json=updated_role)
    assert resp.status_code == OK
    assert resp.json[ep.ROLE_UPDATE_RESP] == 'Role updated!'
    
def test_delete_role():
    resp = TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/TR')
    assert resp.status_code == OK
    assert resp.json[ep.ROLE_DELETE_RESP] == 'Role deleted!'

def test_delete_nonexisent_role():
    resp = TEST_CLIENT.delete(f'{ep.ROLE_DELETE_EP}/NONEXISTENT')
    assert resp.status_code == NOT_FOUND

def test_masthead():
    resp = TEST_CLIENT.get(ep.USER_GET_MASTHEAD)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.USER_GET_MASTHEAD_RESP in resp_json
