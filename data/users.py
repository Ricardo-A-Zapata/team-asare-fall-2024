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

user_dict = {
    TEST_EMAIL: {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: "NYU",
        EMAIL: TEST_EMAIL,
    }
}


def get_users():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user name (a str).
        - Each user name must be the key for a dictionary.
        - That dictionary must at least include a LEVEL member that has an int
        value.
    """
    users = {
        "Callahan": {
            LEVEL: 0,
        },
        "Reddy": {
            LEVEL: 1,
        },
    }
    return users


def create(name: str, email: str, affiliation: str):
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email = }')
    people_dict[email] = {Name: name, EMAIL: email, AFFILIATION: affiliation}


def main():
    pass


if __name__ == '__main__':
    main()
