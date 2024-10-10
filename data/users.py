"""
This module interfaces to our user data.
"""

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


def create(name: str, email: str, affiliation: str):
    if email in users_dict:
        raise ValueError(f'Adding duplicate {email=}')
    users_dict[email] = {NAME: name, EMAIL: email, AFFILIATION: affiliation}
    return email


def main():
    pass


if __name__ == '__main__':
    main()
