"""
This module interfaces to our text data.
"""

# fields
KEY = 'key'
TITLE = 'title'
TEXT = 'text'
EMAIL = 'email'

TEST_KEY = 'HomePage'
SUBM_KEY = 'SubmissionsPage'
DEL_KEY = 'DeletePage'

text_dict = {
    TEST_KEY: {
        TITLE: 'Home Page',
        TEXT: 'This is a journal about building API servers.',
    },
    SUBM_KEY: {
        TITLE: 'Submissions Page',
        TEXT: 'All submissions must be original work in Word format.',
    },
    DEL_KEY: {
        TITLE: 'Delete Page',
        TEXT: 'This is a text to delete.',
    },
}


def create(key: str, title: str, text: str) -> bool:
    """
    Create a new text entry.
    """
    if key in text_dict:
        raise KeyError(f'{key} already exists in journal text')
    text_dict[key] = {TITLE: title, TEXT: text}
    return True


def delete(key: str) -> bool:
    """
    Delete a text entry.
    """
    if key not in text_dict:
        return False
    del text_dict[key]
    return True


def update(key: str, title: str, text: str) -> bool:
    """
    Update an existing text entry.
    """
    if key not in text_dict:
        return False
    text_dict[key] = {TITLE: title, TEXT: text}
    return True


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of text entries keyed on entry key.
        - Each entry key must be the key for another dictionary.
    """
    return text_dict


def read_one(key: str) -> dict:
    """
    This takes a key and returns the page dictionary
    for that key. Return an empty dictionary if key not found.
    """
    result = {}
    if key in text_dict:
        result = text_dict[key]
    return result


def main():
    print(read())


if __name__ == '__main__':
    main()
