"""
This module manages person roles for a journal.
"""
AUTHOR_CODE = 'AU'
EDITOR_CODE = 'ED'
REFEREE_CODE = 'RE'
TEST_CODE = AUTHOR_CODE
ROLES = {
    AUTHOR_CODE: 'Author',
    EDITOR_CODE: 'Editor',
    REFEREE_CODE: 'Referee',
}


def create(code: str, role: str) -> bool:
    """
    Create a new role.
    """
    if code in ROLES:
        raise ValueError(f"Role with code '{code}' already exists.")
    ROLES[code] = role
    return True


def get_roles() -> dict:
    return ROLES


def read_one(code: str) -> str:
    """
    Read a specific role by code.
    """
    return ROLES.get(code)


def is_valid(code: str) -> bool:
    return code in ROLES


def update(code: str, new_role: str) -> bool:
    """
    update existing role
    """
    if code not in ROLES:
        raise ValueError(f"Role with code '{code}' does not exist.")
    ROLES[code] = new_role
    return True


def delete(code: str) -> bool:
    """
    Delete a role.
    """
    if code not in ROLES:
        return False
    del ROLES[code]
    return True
