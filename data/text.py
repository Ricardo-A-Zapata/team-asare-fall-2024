"""
This module interfaces to our text data.
"""
import data.db_connect as dbc

# fields
KEY = 'key'
TITLE = 'title'
TEXT = 'text'
EMAIL = 'email'

TEST_KEY = 'HomePage'
SUBM_KEY = 'SubmissionsPage'
DEL_KEY = 'DeletePage'

TEXT_COLLECTION = 'texts'
TEST_COLLECTION = 'test_texts'

# Initialize DB connection
dbc.connect_db()


def get_collection_name(testing=False):
    """Return the appropriate collection name based on testing flag"""
    return TEST_COLLECTION if testing else TEXT_COLLECTION


def create(key: str, title: str, text: str, testing=False) -> bool:
    """
    Create a new text entry.
    """
    try:
        collection = get_collection_name(testing)
        if dbc.fetch_one(collection, {KEY: key}):
            raise KeyError(f'{key} already exists in journal text')
        text_doc = {
            KEY: key,
            TITLE: title,
            TEXT: text
        }
        dbc.insert_one(collection, text_doc)
        return True
    except Exception as e:
        print(f"Error in create: {str(e)}")
        raise e


def delete(key: str, testing=False) -> bool:
    """
    Delete a text entry.
    Returns True if successful, raises KeyError if not found.
    """
    try:
        collection = get_collection_name(testing)
        text = dbc.fetch_one(collection, {KEY: key})
        if not text:
            raise KeyError(f'Text with key "{key}" not found')
        dbc.del_one(collection, {KEY: key})
        return True
    except KeyError as e:
        raise e
    except Exception as e:
        print(f"Error in delete: {str(e)}")
        return False


def update(key: str, title: str, text: str, testing=False) -> bool:
    """
    Update an existing text entry.
    """
    try:
        collection = get_collection_name(testing)
        if not dbc.fetch_one(collection, {KEY: key}):
            return False
        update_doc = {
            KEY: key,
            TITLE: title,
            TEXT: text
        }
        return bool(dbc.update_doc(collection, {KEY: key}, update_doc))
    except Exception as e:
        print(f"Error in update: {str(e)}")
        return False


def read(testing=False):
    """
    Our contract:
        - Returns a dictionary of text entries keyed on entry key.
        - Each entry key must be the key for another dictionary.
    """
    texts = {}
    try:
        collection = get_collection_name(testing)
        all_texts = dbc.fetch_all(collection)
        for text in all_texts:
            if dbc.MONGO_ID in text:
                del text[dbc.MONGO_ID]
            texts[text[KEY]] = {
                TITLE: text[TITLE],
                TEXT: text[TEXT]
            }
        return texts
    except Exception as e:
        print(f"Error in read: {str(e)}")
        return texts


def read_one(key: str, testing=False) -> dict:
    """
    This takes a key and returns the page dictionary
    for that key. Return an empty dictionary if key not found.
    """
    try:
        collection = get_collection_name(testing)
        text = dbc.fetch_one(collection, {KEY: key})
        if text:
            if dbc.MONGO_ID in text:
                del text[dbc.MONGO_ID]
            return {TITLE: text[TITLE], TEXT: text[TEXT]}
        return {}
    except Exception as e:
        print(f"Error in read_one: {str(e)}")
        return {}


def init_db():
    """
    Initialize the texts collection with test data if it doesn't exist
    """
    test_texts = {
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
    for key, content in test_texts.items():
        if not dbc.fetch_one(TEXT_COLLECTION, {KEY: key}):
            text_doc = {
                KEY: key,
                TITLE: content[TITLE],
                TEXT: content[TEXT]
            }
            dbc.insert_one(TEXT_COLLECTION, text_doc)


# Call initialization
init_db()


def main():
    print(read())


if __name__ == '__main__':
    main()
