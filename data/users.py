"""
This module interfaces to our user data.
"""
import re

import data.roles as rls

LEVEL = 'level'
MIN_USER_NAME_LEN = 2
# fields
NAME = 'name'
ROLES = 'roles'
EMAIL = 'email'
AFFILIATION = 'affiliation'
TEST_EMAIL = 'ejc369@nyu.edu'


users_dict = {
    TEST_EMAIL: {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: "NYU",
        EMAIL: TEST_EMAIL,
    }
}


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user name (a str).
        - Each user name must be the key for a dictionary.
    """
    users = users_dict
    return users


def read_one(email: str):
    return users_dict.get(email)


VALID_CHARS = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]"
CHAR_OR_DIGIT = r"[A-Za-z0-9-]"


def is_valid_email(email: str) -> bool:
    match = re.fullmatch(
        rf'{VALID_CHARS}+@[A-Za-z0-9.-]+\.[A-Za-z]{{2,6}}', email)
    if not match:
        return False
    local_part = email.split('@')[0]
    if local_part.startswith('.') or local_part.endswith('.'):
        return False
    if '..' in local_part:
        return False
    return True


def is_valid_user(name: str, email: str, affiliation: str, role: str = None,
                  roles: list = None) -> bool:
    if email in users_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid Role: {role}')
    elif role:
        for role in roles:
            if not rls.is_valid(role):
                raise ValueError(f'Invalid Role: {role}')
    return True


def create(name: str, email: str, affiliation: str, role: str = None):
    if email in users_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid Role: {role}')
    users_dict[email] = {
                            NAME: name,
                            EMAIL: email,
                            AFFILIATION: affiliation,
                            ROLES: [role] if role else []
                         }
    return email


def update(name: str, email: str, affiliation: str):
    if email in users_dict:
        users_dict[email] = {
                                NAME: name,
                                EMAIL: email,
                                AFFILIATION: affiliation,
                            }
        return True
    return False


def delete(_id: str):
    """
    deletes a user (username) from the dictionary of users, if found.
    returns the username that was deleted, or None if not found.
    """
    users = read()
    if _id in users:
        del users[_id]
        return _id
    raise KeyError(f'ID "{_id} not found')


def has_role(user: dict, role: str) -> bool:
    if role in user.get(ROLES):
        return True
    return False


MH_FIELDS = [NAME, AFFILIATION]


def create_mh_rec(person: dict) -> dict:
    mh_rec = {}
    for field in MH_FIELDS:
        mh_rec[field] = person.get(field, '')
    return mh_rec


def get_masthead() -> dict:
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        user_w_role = []
        users = read()
        for _id, user in users.items():
            if has_role(user, mh_role):
                rec = create_mh_rec(user)
                user_w_role.append(rec)
        masthead[text] = user_w_role
    return masthead


def get_mh_field(email: str, field: str):
    user = users_dict.get(email)
    if user and field in user:
        return user[field]
    return None


def main():
    print(get_masthead())


if __name__ == '__main__':
    main()
