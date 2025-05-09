"""
This module manages person roles for a journal.
"""
import data.db_connect as dbc

# Constants
AUTHOR_CODE = 'AU'
EDITOR_CODE = 'ED'
REFEREE_CODE = 'RE'
ROLES_COLLECTION = 'roles'
USERS_COLLECTION = 'users'
ERROR_KEY = "error"
CODE_KEY = "code"
ROLE_KEY = "role"
ROLE_CODES_KEY = "roleCodes"
ROLES = {
    AUTHOR_CODE: 'Author',
    EDITOR_CODE: 'Editor',
    REFEREE_CODE: 'Referee',
}
MH_ROLES = [AUTHOR_CODE, EDITOR_CODE]


def get_roles(testing=False) -> dict:
    """
    Get all roles from MongoDB as a dictionary.
    """
    roles = {}
    try:
        all_roles = dbc.fetch_all(ROLES_COLLECTION, testing=testing)
        for role in all_roles:
            roles[role.get(CODE_KEY)] = role.get(ROLE_KEY)
        return roles
    except Exception as e:
        print(f"Error in get_roles: {str(e)}")
        return {}


def create(code: str, role: str, testing=False):
    """
    Create a new role in MongoDB, with safeguards for test roles.
    """
    try:
        if dbc.fetch_one(ROLES_COLLECTION, {CODE_KEY: code}, testing=testing):
            raise ValueError(f"Role with code '{code}' already exists.")

        dbc.insert_one(ROLES_COLLECTION, {
            CODE_KEY: code,
            ROLE_KEY: role
            }, testing=testing)
        return True
    except Exception as e:
        print(f"Error in create: {str(e)}")
        raise e


def seed_roles(testing=False):
    """
    Seed the default roles into the roles collection.
    """
    try:
        collection = ROLES_COLLECTION
        if testing:
            collection += "_test"  # Ensure testing uses the test collection

        existing_roles = get_roles(testing=testing)
        for code, role in ROLES.items():
            if code not in existing_roles:
                create(code, role, testing=testing)
    except Exception as e:
        print(f"Error in seeding roles: {str(e)}")


dbc.connect_db()
seed_roles()


def read_one(code: str, testing=False) -> str:
    """
    Read a specific role by its code from MongoDB.
    """
    try:
        role = dbc.fetch_one(
            ROLES_COLLECTION,
            {CODE_KEY: code},
            testing=testing
            )
        return role.get(ROLE_KEY) if role else None
    except Exception as e:
        print(f"Error in read_one: {str(e)}")
        return None


def update(code: str, new_role: str, testing=False) -> bool:
    """
    Update an existing role in MongoDB.
    """
    try:
        if not read_one(code, testing=testing):
            raise ValueError(f"Role with code '{code}' does not exist.")
        return bool(dbc.update_doc(
            ROLES_COLLECTION, {CODE_KEY: code}, {ROLE_KEY: new_role},
            testing=testing))
    except Exception as e:
        print(f"Error in update: {str(e)}")
        raise e


def delete(code: str, testing=False) -> dict:
    """
    Delete a role by its code from MongoDB, remove it from all users,
    and return details of the deleted role.
    """
    try:

        role = dbc.fetch_one(ROLES_COLLECTION, {
            CODE_KEY: code}, testing=testing)
        if not role:
            return None

        # Delete the role from the roles collection
        dbc.del_one(ROLES_COLLECTION, {CODE_KEY: code}, testing=testing)

        # Remove the role code from all users
        dbc.client[dbc.JOURNAL_DB][USERS_COLLECTION].update_many(
            {ROLE_CODES_KEY: code},
            {"$pull": {ROLE_CODES_KEY: code}}
        )

        return role
    except Exception as e:
        print(f"Error in delete: {str(e)}")
        raise e


def get_masthead_roles() -> dict:
    """
    Get masthead roles (filtered subset of all roles).
    """
    masthead_roles = {}
    try:
        all_roles = get_roles()
        for code, role in all_roles.items():
            if code in MH_ROLES:
                masthead_roles[code] = role
        return masthead_roles
    except Exception as e:
        print(f"Error in get_masthead_roles: {str(e)}")
        return masthead_roles


def is_valid(code: str, testing=False) -> bool:
    """
    Check if a role with the given code exists in MongoDB.
    """
    try:
        return (dbc.fetch_one(ROLES_COLLECTION, {CODE_KEY: code},
                              testing=testing) is not None)
    except Exception as e:
        print(f"Error in is_valid: {str(e)}")
        return False
