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
MH_ROLES = [AUTHOR_CODE, EDITOR_CODE, REFEREE_CODE]


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


def get_masthead_roles() -> dict:
    mh_roles = get_roles()
    del_mh_roles = []
    for role in mh_roles:
        if role not in MH_ROLES:
            del_mh_roles.append(role)
    for del_role in del_mh_roles:
        del mh_roles[del_role]
    return mh_roles


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
