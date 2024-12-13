"""
This file contains the manuscript data and operations.
"""

from typing import Dict, Optional
from datetime import datetime
import data.db_connect as db
from bson import ObjectId

# Constants for manuscript fields
TITLE = 'title'
AUTHOR = 'author'
AUTHOR_EMAIL = 'author_email'
STATE = 'state'
REFEREES = 'referees'
TEXT = 'text'
ABSTRACT = 'abstract'
HISTORY = 'history'
EDITOR = 'editor'
REPORT = 'report'
VERDICT = 'verdict'

STATE_SUBMITTED = 'SUBMITTED'
STATE_REFEREE_REVIEW = 'REFEREE_REVIEW'
STATE_REJECTED = 'REJECTED'
STATE_AUTHOR_REVISIONS = 'AUTHOR_REVISIONS'
STATE_EDITOR_REVIEW = 'EDITOR_REVIEW'
STATE_COPY_EDIT = 'COPY_EDIT'
STATE_AUTHOR_REVIEW = 'AUTHOR_REVIEW'
STATE_FORMATTING = 'FORMATTING'
STATE_PUBLISHED = 'PUBLISHED'
STATE_WITHDRAWN = 'WITHDRAWN'

VALID_STATES = {
    STATE_SUBMITTED,
    STATE_REFEREE_REVIEW,
    STATE_REJECTED,
    STATE_AUTHOR_REVISIONS,
    STATE_EDITOR_REVIEW,
    STATE_COPY_EDIT,
    STATE_AUTHOR_REVIEW,
    STATE_FORMATTING,
    STATE_PUBLISHED,
    STATE_WITHDRAWN
}

VERDICT_ACCEPT = 'ACCEPT'
VERDICT_ACCEPT_WITH_REVISIONS = 'ACCEPT_W_REV'
VERDICT_REJECT = 'REJECT'

# In-memory storage (will be replaced with MongoDB)
manuscripts: Dict = {}
MANUSCRIPTS_COLLECTION = "manuscripts"

db.connect_db()  # connect to MongoDB


def get_collection_name(testing=False):
    """Return the collection name - always manuscripts"""
    return MANUSCRIPTS_COLLECTION


def create_manuscript(
    title: str,
    author: str,
    author_email: str,
    text: str,
    abstract: str
) -> dict:
    """
    Create a new manuscript entry and insert it into the database.
    """
    try:
        timestamp = datetime.now().isoformat()
        manuscript = {
            TITLE: title,
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            STATE: STATE_SUBMITTED,
            REFEREES: {},
            TEXT: text,
            ABSTRACT: abstract,
            HISTORY: [{
                'state': STATE_SUBMITTED,
                'timestamp': timestamp,
                'actor': author_email
            }],
            EDITOR: None
        }

        collection = get_collection_name()
        result = db.insert_one(collection, manuscript)
        manuscript['_id'] = str(result.inserted_id)
        return manuscript
    except Exception as e:
        print(f"Error in create_manuscript: {str(e)}")
        raise e


def get_manuscript(manuscript_id: str, testing=False) -> Optional[dict]:
    """
    Retrieve a manuscript by ID from MongoDB.
    """
    try:
        collection = get_collection_name(testing)
        manuscript = db.fetch_one(
            collection, {"_id": ObjectId(manuscript_id)}
        )
        if manuscript:
            manuscript['_id'] = str(manuscript['_id'])
        return manuscript
    except Exception as e:
        print(f"Error fetching manuscript: {e}")
        return None


def update_state(
    manuscript_id: str,
    new_state: str,
    actor_email: str
) -> Optional[dict]:
    """
    Update the state of a manuscript and record in history.
    """
    if new_state not in VALID_STATES:
        print(f"Invalid state: {new_state}")
        return None

    try:
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return None

        # Create update data without _id field
        manuscript_id_obj = manuscript['_id']
        del manuscript['_id']
        manuscript[STATE] = new_state
        manuscript[HISTORY].append({
            'state': new_state,
            'timestamp': datetime.now().isoformat(),
            'actor': actor_email
        })

        # Update in database
        db.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id_obj)},
            manuscript
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error updating state: {e}")
        return None


def assign_editor(
    manuscript_id: str,
    editor_email: str
) -> Optional[dict]:
    """
    Assign an editor to a manuscript.
    """
    manuscript = get_manuscript(manuscript_id)
    if not manuscript:
        return None
    manuscript[EDITOR] = editor_email
    try:
        db.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            manuscript
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error assigning editor: {e}")
        return None


def editor_move(
    manuscript_id: str,
    target_state: str,
    editor_email: str
) -> Optional[dict]:
    """
    Editor is able to move manuscript to any state
    """
    return update_state(manuscript_id, target_state, editor_email)


def author_withdraw(manuscript_id: str, author_email: str) -> Optional[dict]:
    return update_state(manuscript_id, STATE_WITHDRAWN, author_email)


def get_referee_verdict(manuscript_id: str) -> Optional[str]:
    """
    returns referee's verdict message.
    """
    manuscript = get_manuscript(manuscript_id)
    if manuscript and "verdict" in manuscript:
        return manuscript["verdict"]
    return None


def reject_manuscript(manuscript_id: str, actor_email: str) -> Optional[dict]:
    """
    rejects manuscript if referee's verdict is REJECT
    """
    verdict = get_referee_verdict(manuscript_id)
    if verdict == VERDICT_REJECT:
        return update_state(manuscript_id, STATE_REJECTED, actor_email)
    else:
        return {"error:", "No reject verdict"}


def get_all_manuscripts(testing=False) -> Dict:
    """
    Get all manuscripts from database.
    """
    manuscripts = {}
    try:
        collection = get_collection_name(testing)
        all_manuscripts = db.fetch_all(collection)
        for manuscript in all_manuscripts:
            if '_id' in manuscript:
                manuscript['_id'] = str(manuscript['_id'])
            manuscripts[manuscript['_id']] = manuscript
        return manuscripts
    except Exception as e:
        print(f"Error fetching all manuscripts: {e}")
        return manuscripts


def delete_manuscript(manuscript_id: str) -> Optional[dict]:
    """
    Delete a manuscript by ID from database.
    Returns the deleted manuscript if successful, None if not found.
    """
    try:
        manuscript = get_manuscript(manuscript_id)
        if manuscript:
            db.del_one(
                MANUSCRIPTS_COLLECTION,
                {"_id": ObjectId(manuscript_id)}
            )
        return manuscript
    except Exception as e:
        print(f"Error deleting manuscript: {e}")
        return None


def accept_manuscript(manuscript_id: str, actor_email: str) -> Optional[dict]:
    """
    Accept manuscript, moving it to the next state based on current state.
    If in AUTHOR_REVISIONS or REFEREE_REVIEW, move to COPY_EDIT.
    If in EDITOR_REVIEW, move to PUBLISHED.
    """
    manuscript = get_manuscript(manuscript_id)
    if not manuscript:
        return None
    current_state = manuscript[STATE]
    if (current_state == STATE_AUTHOR_REVISIONS or
            current_state == STATE_REFEREE_REVIEW):
        return update_state(manuscript_id, STATE_COPY_EDIT, actor_email)
    elif current_state == STATE_EDITOR_REVIEW:
        return update_state(manuscript_id, STATE_PUBLISHED, actor_email)
    else:
        return None


def accept_with_revisions(
    manuscript_id: str, actor_email: str
) -> Optional[dict]:
    """
    Move manuscript to AUTHOR_REVISIONS after review.
    """
    return update_state(manuscript_id, STATE_AUTHOR_REVISIONS, actor_email)


def save_manuscript(manuscript: dict) -> None:
    """
    Save a manuscript to MongoDB.
    """
    db.insert_one(MANUSCRIPTS_COLLECTION, manuscript)


def add_referee_report(
    manuscript_id: str,
    referee_email: str,
    report: str,
    verdict: str
) -> Optional[dict]:
    """
    Add a referee report to a manuscript
    """
    if verdict not in [
        VERDICT_ACCEPT,
        VERDICT_ACCEPT_WITH_REVISIONS,
        VERDICT_REJECT
    ]:
        raise ValueError(f"Invalid verdict: {verdict}")

    try:
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return None

        # Remove _id for update
        manuscript_id_obj = manuscript['_id']
        del manuscript['_id']

        referees = manuscript.get(REFEREES, {})
        referees[referee_email] = {
            REPORT: report,
            VERDICT: verdict
        }
        manuscript[REFEREES] = referees

        db.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id_obj)},
            manuscript
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error updating referee report: {e}")
        return None


def assign_referee(manuscript_id: str, referee_email: str) -> Optional[dict]:
    """
    Assign a referee to a manuscript
    """
    try:
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return None

        # Remove _id for update
        manuscript_id_obj = manuscript['_id']
        del manuscript['_id']

        referees = manuscript.get(REFEREES, {})
        referees[referee_email] = {}
        manuscript[REFEREES] = referees

        db.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id_obj)},
            manuscript
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error assigning referee: {e}")
        return None


def remove_referee(manuscript_id: str, referee_email: str) -> Optional[dict]:
    """
    Remove a referee from a manuscript
    """
    try:
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return None

        # Remove _id for update
        manuscript_id_obj = manuscript['_id']
        del manuscript['_id']

        referees = manuscript.get(REFEREES, {})
        if referee_email in referees:
            del referees[referee_email]
        manuscript[REFEREES] = referees

        db.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id_obj)},
            manuscript
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error removing referee: {e}")
        return None


def submit_author_approval(
    manuscript_id: str,
    author_email: str
) -> Optional[dict]:
    """
    Author approves changes and moves manuscript to formatting
    """
    manuscript = get_manuscript(manuscript_id)
    if not manuscript or manuscript[STATE] != STATE_AUTHOR_REVIEW:
        return None
    return update_state(manuscript_id, STATE_FORMATTING, author_email)


def complete_formatting(
    manuscript_id: str,
    editor_email: str
) -> Optional[dict]:
    """
    Complete formatting and move to published state
    """
    manuscript = get_manuscript(manuscript_id)
    if not manuscript or manuscript[STATE] != STATE_FORMATTING:
        return None
    return update_state(manuscript_id, STATE_PUBLISHED, editor_email)


def complete_copy_edit(
    manuscript_id: str,
    editor_email: str
) -> Optional[dict]:
    """
    Complete copy editing and move to author review
    """
    manuscript = get_manuscript(manuscript_id)
    if not manuscript or manuscript[STATE] != STATE_COPY_EDIT:
        return None
    return update_state(manuscript_id, STATE_AUTHOR_REVIEW, editor_email)


def validate_state_transition(current_state: str, new_state: str) -> bool:
    """
    Validate if a state transition is allowed according to workflow rules
    """
    valid_transitions = {
        STATE_SUBMITTED: {
            STATE_REFEREE_REVIEW,
            STATE_REJECTED,
            STATE_WITHDRAWN
        },
        STATE_REFEREE_REVIEW: {
            STATE_COPY_EDIT,
            STATE_AUTHOR_REVISIONS,
            STATE_REJECTED,
            STATE_WITHDRAWN
        },
        STATE_AUTHOR_REVISIONS: {
            STATE_COPY_EDIT,
            STATE_WITHDRAWN
        },
        STATE_EDITOR_REVIEW: {
            STATE_COPY_EDIT,
            STATE_WITHDRAWN
        },
        STATE_COPY_EDIT: {
            STATE_AUTHOR_REVIEW,
            STATE_WITHDRAWN
        },
        STATE_AUTHOR_REVIEW: {
            STATE_FORMATTING,
            STATE_WITHDRAWN
        },
        STATE_FORMATTING: {
            STATE_PUBLISHED,
            STATE_WITHDRAWN
        }
    }
    return new_state in valid_transitions.get(current_state, set())
