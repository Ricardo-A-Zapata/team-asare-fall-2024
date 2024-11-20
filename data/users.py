"""
This module interfaces to our user data.
"""
import re

import data.roles as rls
import data.db_connect as dbc

LEVEL = 'level'
MIN_USER_NAME_LEN = 2
# fields
NAME = 'name'
ROLES = 'roles'
EMAIL = 'email'
AFFILIATION = 'affiliation'
TEST_EMAIL = 'ejc369@nyu.edu'
TEST_COLLECTION = 'test_users'

# Initialize DB connection
dbc.connect_db()


def init_db():
    """
    Initialize the users collection with test data if it doesn't exist
    """
    test_user = {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: "NYU",
        EMAIL: TEST_EMAIL,
    }
    if not dbc.fetch_one(dbc.USERS_COLLECTION, {EMAIL: TEST_EMAIL}):
        dbc.insert_one(dbc.USERS_COLLECTION, test_user)


# Call initialization
init_db()


def get_collection_name(testing=False):
    """Return the appropriate collection name based on testing flag"""
    return TEST_COLLECTION if testing else dbc.USERS_COLLECTION


def read(testing=False):
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user name (a str).
        - Each user name must be the key for a dictionary.
    Read all users from MongoDB.
    Returns a dictionary of users keyed by email.
    """
    users = users_dict
    users = {}
    collection = get_collection_name(testing)
    all_users = dbc.fetch_all(collection)
    for user in all_users:
        if dbc.MONGO_ID in user:
            del user[dbc.MONGO_ID]
        users[user[EMAIL]] = user
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


def is_valid_user(
        name: str,
        email: str,
        affiliation: str,
        role: str = None,
        roles: list = None
) -> bool:
    """
    Validate user data before creation/update
    """
    if not name or len(name) < MIN_USER_NAME_LEN:
        raise ValueError(f'Name must be least {MIN_USER_NAME_LEN} characters')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not affiliation:
        raise ValueError('Affiliation cannot be empty')
    if role and not rls.is_valid(role):
        raise ValueError(f'Invalid Role: {role}')
    if roles:
        for r in roles:
            if not rls.is_valid(r):
                raise ValueError(f'Invalid Role: {r}')
    return True


def create(name: str, email: str, affiliation: str, testing=False):
    """
    Create a new user in MongoDB.
    First validates the user data, then inserts if valid.
    """
    try:
        # First validate the user data
        if not is_valid_user(name, email, affiliation):
            raise ValueError("Invalid user data")

        # Check for existing user
        collection = get_collection_name(testing)
        existing = dbc.fetch_one(collection, {EMAIL: email})
        if existing:
            msg = f"User with email {email} already exists"
            raise ValueError(msg)

        # Create new user
        user_doc = {
            NAME: name,
            EMAIL: email,
            AFFILIATION: affiliation,
            ROLES: []  # Initialize with empty roles
        }
        dbc.insert_one(collection, user_doc)
        return email
    except Exception as e:
        print(f"Error in create: {str(e)}")
        raise ValueError(str(e))


def delete(_id: str, testing=False):
    """
    Delete a user by email from MongoDB.
    Returns the deleted email if successful, raises KeyError if not found.
    """
    try:
        collection = get_collection_name(testing)
        user = dbc.fetch_one(collection, {EMAIL: _id})
        if not user:
            raise KeyError(f'User with email "{_id}" not found')
        dbc.del_one(collection, {EMAIL: _id})
        return _id
    except KeyError as e:
        raise e
    except Exception as e:
        print(f"Error in delete: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")


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


def clean_mongo_doc(doc):
    """
    Remove MongoDB-specific fields from a document
    """
    if doc and dbc.MONGO_ID in doc:
        del doc[dbc.MONGO_ID]
    return doc


def main():
    print(get_masthead())


if __name__ == '__main__':
    main()
