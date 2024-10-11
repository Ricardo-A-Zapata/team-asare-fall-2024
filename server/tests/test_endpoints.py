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
        "NAME": "test_user",
        "EMAIL": "test@user.com",
        "AFFILIATION": "Test Uni"
    }
    resp = TEST_CLIENT.put('/user/create', json=test)
    assert resp.status_code == 200
    assert resp.json['Message'] == 'User added!'


def test_read_users():
    resp = TEST_CLIENT.get(ep.USER_READ_EP)
    assert resp.status_code == 200
    resp_json = resp.get_json()
    assert ep.USER_READ_RESP in resp_json
    assert isinstance(resp_json[ep.USER_READ_RESP], dict)
    # Optionally, verify that the test user is in the response
    assert ep.usr.TEST_EMAIL in resp_json[ep.USER_READ_RESP]


def test_delete():
    user_id = 000  # test ID

    # test deletion for existing user
    resp = TEST_CLIENT.delete(f'/user/create/{user_id}')
    assert resp.status_code == 200
    assert resp.json is not None, resp.json['Message'] == 'User deleted!'

    # test deletion for nonexistent user
    resp = TEST_CLIENT.delete(f'/user/create/{user_id}')
    assert resp.status_code == NOT_FOUND
    assert 'No such user' in resp.json['Message']
