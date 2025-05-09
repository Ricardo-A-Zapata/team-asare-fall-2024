"""
This module interfaces to our user data.
"""
import re
import data.roles as rls
import data.db_connect as dbc

# fields
NAME = 'name'
ROLES = 'roleCodes'
EMAIL = 'email'
PASSWORD = 'password'
AFFILIATION = 'affiliation'
TEST_EMAIL = 'ejc369@nyu.edu'

MONGO_ID_KEY = '_id'
ERROR_KEY = 'error'
ROLE_CODES_KEY = 'roleCodes'

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
        password: str,
        affiliation: str,
        roles: list = None,
        testing=False,
        ):
    """
    Create a new user in MongoDB.
    First validates the user data, then inserts if valid.
    """
    try:
        # Validate user data
        if not is_valid_user(name, email, affiliation):
            raise ValueError("Invalid user data")

        # Validate roles
        if roles:
            # Fetch valid roles from the roles collection
            valid_roles = rls.get_roles(testing=testing)
            for role in roles:
                if role not in valid_roles:
                    raise ValueError(f"Invalid role code: {role}")

        # Check for duplicate user
        collection = get_collection_name(testing)
        if dbc.fetch_one(collection, {EMAIL: email}):
            raise ValueError(f"User with email {email} already exists")
        # Create user document
        user_doc = {
            NAME: name,
            EMAIL: email,
            PASSWORD: password,
            AFFILIATION: affiliation,
            ROLES: roles if roles is not None else [],
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
            users[user.get(EMAIL)] = user
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
        testing=False,
        roleCodes: list = None):
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
            update_doc[ROLES] = existing.get(ROLES, [])
        else:
            update_doc[ROLES] = []
        # Add roleCodes if provided
        if roleCodes is not None:
            update_doc[ROLE_CODES_KEY] = roleCodes
        elif ROLE_CODES_KEY in existing:
            update_doc[ROLE_CODES_KEY] = existing.get(ROLE_CODES_KEY, [])
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
    VALID_CHARS = r"[A-Za-z0-9!#$%&'*+/=?^_{|}~.-]"
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
            if ROLES in user and role_code in user.get(ROLES, []):
                users_with_role.append({
                    NAME: user.get(NAME, ''),
                    AFFILIATION: user.get(AFFILIATION, ''),
                    EMAIL: user.get(EMAIL, '')
                })
        masthead[role_text] = users_with_role
    return masthead


def has_role(user: dict, role: str) -> bool:
    """Check if a user has a specific role"""
    if ROLES in user and role in user.get(ROLES, []):
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

        if role not in user.get(ROLES, []):
            user[ROLES].append(role)
            return bool(dbc.update_doc(collection, {EMAIL: email}, user))
        return True
    except Exception as e:
        print(f"Error in add_role: {str(e)}")
        raise e


def login(email: str, password: str) -> bool:
    try:
        user = read_one(email)
        if not user:
            raise KeyError(f'User with email "{email}" not found')
        return user.get(PASSWORD) == password
    except Exception as e:
        print(f"Error in login: {str(e)}")
        raise e


def remove_role(email: str, role: str, testing=False) -> bool:
    """
    Remove a role from a user.
    Returns True if successful, raises KeyError if user not found
    or role does not exist.
    """
    try:
        collection = get_collection_name(testing)
        user = read_one(email, testing)
        if not user:
            raise KeyError(f'User with email "{email}" not found')

        if ROLES not in user or role not in user.get(ROLES, []):
            raise ValueError(f'Role "{role}" not found for user {email}')

        user_roles = user.get(ROLES, [])
        user_roles.remove(role)
        user[ROLES] = user_roles
        return bool(dbc.update_doc(collection, {EMAIL: email}, user))
    except Exception as e:
        print(f"Error in remove_role: {str(e)}")
        raise e


def change_password(email: str, password: str, testing=False) -> bool:
    try:
        collection = get_collection_name(testing)
        existing = dbc.fetch_one(collection, {EMAIL: email})
        if not existing:
            raise KeyError(f"User with email {email} not found")

        update_doc = {
            EMAIL: email,
            PASSWORD: password,
        }
        return bool(dbc.update_doc(collection, {EMAIL: email}, update_doc))
    except Exception as e:
        print(f"Error in update: {str(e)}")
        raise e
