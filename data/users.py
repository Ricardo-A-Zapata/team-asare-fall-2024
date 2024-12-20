"""
This module interfaces to our user data.
"""
import re
import data.roles as rls
import data.db_connect as dbc

# fields
NAME = 'name'
ROLES = 'roles'
EMAIL = 'email'
AFFILIATION = 'affiliation'
TEST_EMAIL = 'ejc369@nyu.edu'

USERS_COLLECTION = 'users'

MIN_USER_NAME_LEN = 2

# Initialize DB connection
dbc.connect_db()


def get_collection_name(testing=False):
    """Return the collection name - always users"""
    return USERS_COLLECTION


def create(
        name: str,
        email: str,
        affiliation: str,
        roles: list = None,
        testing=False):
    """
    Create a new user in MongoDB.
    First validates the user data, then inserts if valid.
    """
    try:
        if not is_valid_user(name, email, affiliation):
            raise ValueError("Invalid user data")

        collection = get_collection_name(testing)
        if dbc.fetch_one(collection, {EMAIL: email}):
            raise ValueError(f"User with email {email} already exists")

        user_doc = {
            NAME: name,
            EMAIL: email,
            AFFILIATION: affiliation,
            ROLES: roles if roles is not None else []
        }
        dbc.insert_one(collection, user_doc)
        return email
    except Exception as e:
        print(f"Error in create: {str(e)}")
        raise e


def read(testing=False):
    """
    Read all users from MongoDB.
    Returns a dictionary of users keyed by email.
    """
    users = {}
    try:
        collection = get_collection_name(testing)
        all_users = dbc.fetch_all(collection)
        for user in all_users:
            if dbc.MONGO_ID in user:
                del user[dbc.MONGO_ID]
            users[user[EMAIL]] = user
        return users
    except Exception as e:
        print(f"Error in read: {str(e)}")
        return users


def read_one(email: str, testing=False):
    """
    Read a single user from MongoDB.
    Returns None if user not found.
    """
    try:
        collection = get_collection_name(testing)
        user = dbc.fetch_one(collection, {EMAIL: email})
        if user and dbc.MONGO_ID in user:
            del user[dbc.MONGO_ID]
        return user
    except Exception as e:
        print(f"Error in read_one: {str(e)}")
        return None


def update(
        name: str,
        email: str,
        affiliation: str,
        roles: list = None,
        testing=False):
    """
    Update an existing user in MongoDB.
    Email serves as the unique identifier and cannot be changed.
    """
    try:
        if not is_valid_user(name, email, affiliation):
            raise ValueError("Invalid user data")

        collection = get_collection_name(testing)
        existing = dbc.fetch_one(collection, {EMAIL: email})
        if not existing:
            raise KeyError(f"User with email {email} not found")

        update_doc = {
            NAME: name,
            EMAIL: email,
            AFFILIATION: affiliation,
        }
        # Only update roles if provided
        if roles is not None:
            update_doc[ROLES] = roles
        elif ROLES in existing:
            update_doc[ROLES] = existing[ROLES]
        else:
            update_doc[ROLES] = []

        return bool(dbc.update_doc(collection, {EMAIL: email}, update_doc))
    except Exception as e:
        print(f"Error in update: {str(e)}")
        raise e


def delete(email: str, testing=False):
    """
    Delete a user by email from MongoDB.
    Returns the deleted email if successful, raises KeyError if not found.
    """
    try:
        collection = get_collection_name(testing)
        user = dbc.fetch_one(collection, {EMAIL: email})
        if not user:
            raise KeyError(f'User with email "{email}" not found')
        dbc.del_one(collection, {EMAIL: email})
        return email
    except Exception as e:
        print(f"Error in delete: {str(e)}")
        raise e


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    VALID_CHARS = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]"
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


def is_valid_user(name: str, email: str, affiliation: str) -> bool:
    """Validate user data before creation/update"""
    if not name or len(name) < MIN_USER_NAME_LEN:
        raise ValueError(f'Name must be least {MIN_USER_NAME_LEN} characters')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not affiliation:
        raise ValueError('Affiliation cannot be empty')
    return True


def get_masthead():
    """Get masthead information"""
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for role_code, role_text in mh_roles.items():
        users_with_role = []
        all_users = read()
        for user in all_users.values():
            if ROLES in user and role_code in user[ROLES]:
                users_with_role.append({
                    NAME: user[NAME],
                    AFFILIATION: user[AFFILIATION]
                })
        masthead[role_text] = users_with_role
    return masthead


def has_role(user: dict, role: str) -> bool:
    """Check if a user has a specific role"""
    if ROLES in user and role in user[ROLES]:
        return True
    return False


def create_mh_rec(person: dict) -> dict:
    """Create a masthead record from a user record"""
    mh_rec = {}
    for field in [NAME, AFFILIATION]:
        mh_rec[field] = person.get(field, '')
    return mh_rec


def add_role(email: str, role: str, testing=False) -> bool:
    """
    Add a role to a user.
    Returns True if successful, raises KeyError if user not found.
    """
    try:
        collection = get_collection_name(testing)
        user = read_one(email, testing)
        if not user:
            raise KeyError(f'User with email "{email}" not found')

        if ROLES not in user:
            user[ROLES] = []

        if role not in user[ROLES]:
            user[ROLES].append(role)
            return bool(dbc.update_doc(collection, {EMAIL: email}, user))
        return True
    except Exception as e:
        print(f"Error in add_role: {str(e)}")
        raise e
