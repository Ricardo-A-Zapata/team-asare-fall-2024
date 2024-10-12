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
        "affiliation": "Test Uni"
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
    # assert resp_json[ep.USER_UPDATE_EP] == True
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
    "affiliation": "Random Uni to Test"
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