"""
This module interfaces to our user data.
"""
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


def is_valid_email(email: str) -> bool:
    return True
    # TODO: Yush will implement regex for this function


def is_valid_user(name: str, email: str, affiliation: str, role: str):
    if email in users_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not rls.is_valid(role):
        raise ValueError(f'Invalid role: {role}')
    return True


def create(name: str, email: str, affiliation: str):
    if email in users_dict:
        raise ValueError(f'Adding duplicate {email=}')
    users_dict[email] = {
                            NAME: name,
                            EMAIL: email,
                            AFFILIATION: affiliation,
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


def main():
    pass


if __name__ == '__main__':
    main()
