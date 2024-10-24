"""
This module manages person roles for a journal.
"""
AUTHOR_CODE = 'AU'
EDITOR_CODE = 'ED'
REFEREE_CODE = 'RE'
ROLES = {
    AUTHOR_CODE: 'Author',
    EDITOR_CODE: 'Editor',
    REFEREE_CODE: 'Referee',
}
def get_roles() -> dict:
    return ROLES
def is_valid(code: str) -> bool:
    return code in ROLES