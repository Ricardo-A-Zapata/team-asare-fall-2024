"""
This file contains the manuscript data and operations.
"""

from typing import Dict, Optional
from datetime import datetime
import data.db_connect as dbc
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

MANUSCRIPTS_COLLECTION = 'manuscripts'

dbc.connect_db()  # connect to MongoDB


def get_collection_name(testing=False):
    """Return the collection name - always manuscripts"""
    return MANUSCRIPTS_COLLECTION


def create_manuscript(
    title: str,
    author: str,
    author_email: str,
    text: str,
    abstract: str,
    testing=False
) -> dict:
    """
    Create a new manuscript entry and insert it into the MongoDB collection.
    """
    try:
        collection = get_collection_name(testing)
        if dbc.fetch_one(
            MANUSCRIPTS_COLLECTION,
            {TITLE: title, AUTHOR_EMAIL: author_email}
        ):
            raise ValueError(
                f"Manuscript with title '{title}' and author email "
                f"'{author_email}' already exists"
            )

        timestamp = datetime.now().isoformat()
        manuscript = {
            TITLE: title,
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            STATE: STATE_SUBMITTED,
            REFEREES: {},  # Referees are initially empty
            TEXT: text,
            ABSTRACT: abstract,
            HISTORY: [
                {
                    "state": STATE_SUBMITTED,
                    "timestamp": timestamp,
                    "actor": author_email,
                }
            ],
            EDITOR: None,  # No editor assigned yet
        }

        # Insert the manuscript and retrieve the inserted ID
        result = dbc.insert_one(collection, manuscript)
        manuscript["_id"] = str(result.inserted_id)
        return manuscript

    except Exception as e:
        print(f"Error in create: {str(e)}")
        raise e


def get_manuscript(manuscript_id: str, testing=False) -> Optional[dict]:
    """
    Retrieve a manuscript by ID from MongoDB.
    """
    try:
        collection = get_collection_name(testing)
        manuscript = dbc.fetch_one(
            collection, {"_id": ObjectId(manuscript_id)}, testing=testing
        )
        if manuscript:
            manuscript['_id'] = str(manuscript['_id'])
        return manuscript
    except Exception as e:
        print(f"Error fetching manuscript: {e}")
        return {"error": f"Invalid manuscript ID or not found: {str(e)}"}


def update_state(
    manuscript_id: str,
    new_state: str,
    actor_email: str
) -> Optional[dict]:
    """
    Update the state of a manuscript and record in history.
    """
    try:
        # Fetch the manuscript
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return {"error": "Manuscript not found"}

        # Validate the state transition
        current_state = manuscript[STATE]
        if not validate_state_transition(current_state, new_state):
            return {
                "error": f"Invalid state transition from {
                    current_state} to {new_state}"
            }

        # Update state and history
        manuscript[STATE] = new_state
        manuscript[HISTORY].append({
            "state": new_state,
            "timestamp": datetime.now().isoformat(),
            "actor": actor_email
        })

        # Save the updated manuscript in the database
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": {STATE: new_state, HISTORY: manuscript[HISTORY]}}
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error updating state: {e}")
        return {"error": f"An error occurred: {str(e)}"}


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
        dbc.update_doc(
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


def author_withdraw(
        manuscript_id: str, author_email: str) -> Optional[dict]:
    return update_state(manuscript_id, STATE_WITHDRAWN, author_email)


def get_referee_verdict(manuscript_id: str) -> Optional[str]:
    """
    returns referee's verdict message.
    """
    manuscript = get_manuscript(manuscript_id)
    if manuscript and "verdict" in manuscript:
        return manuscript["verdict"]
    return None


def reject_manuscript(
        manuscript_id: str, actor_email: str) -> Optional[dict]:
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
        all_manuscripts = dbc.fetch_all(collection)
        for manuscript in all_manuscripts:
            if '_id' in manuscript:
                manuscript['_id'] = str(manuscript['_id'])
            manuscripts[manuscript['_id']] = manuscript
        return manuscripts
    except Exception as e:
        print(f"Error fetching all manuscripts: {e}")
        return manuscripts


def delete_manuscript(manuscript_id: str, testing=False) -> Optional[dict]:
    """
    Delete a manuscript by ID from database.
    Returns the deleted manuscript if successful, None if not found.
    """
    try:
        manuscript = get_manuscript(manuscript_id, testing=testing)
        if manuscript:
            dbc.del_one(
                MANUSCRIPTS_COLLECTION,
                {"_id": ObjectId(manuscript_id)},
                db=dbc.JOURNAL_DB,
                testing=testing
            )
            return manuscript
        else:
            return {"error": "Manuscript not found"}
    except Exception as e:
        print(f"Error deleting manuscript: {e}")
        return {"error": f"Invalid manuscript ID or not found: {str(e)}"}


def accept_manuscript(
        manuscript_id: str, actor_email: str) -> Optional[dict]:
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
    dbc.insert_one(MANUSCRIPTS_COLLECTION, manuscript)


def add_referee_report(
    manuscript_id: str,
    referee_email: str,
    report: str,
    verdict: str,
    testing=False
) -> Optional[dict]:
    """
    Add a referee report to a manuscript.
    """
    if verdict not in [
        VERDICT_ACCEPT,
        VERDICT_ACCEPT_WITH_REVISIONS,
        VERDICT_REJECT
    ]:
        return {"error": f"Invalid verdict: {verdict}"}

    try:
        manuscript = get_manuscript(manuscript_id, testing=testing)
        if not manuscript:
            return {"error": "Manuscript not found"}

        referees = manuscript.get(REFEREES, {})
        if referee_email not in referees:
            return {"error": "Referee not assigned to this manuscript"}

        referees[referee_email] = {
            REPORT: report,
            VERDICT: verdict
        }
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": {REFEREES: referees}},
            db=dbc.JOURNAL_DB,
            testing=testing
        )
        return get_manuscript(manuscript_id, testing=testing)
    except Exception as e:
        print(f"Error updating referee report: {e}")
        return {"error": f"An error occurred: {str(e)}"}


def assign_referee(manuscript_id: str, referee_email: str) -> Optional[dict]:
    """
    Assign a referee to a manuscript
    """
    try:
        # Fetch manuscript and referee details
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return {"error": "Manuscript not found"}

        referee = dbc.fetch_one("users", {"email": referee_email})
        if not referee or "RE" not in referee.get("roleCodes", []):
            return {"error": "Referee not found or does not have the RE role"}

        # Update referees field
        updated_referees = manuscript.get(REFEREES, {})
        if referee_email in updated_referees:
            return {"error": "Referee already assigned"}

        updated_referees[referee_email] = {}
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": {REFEREES: updated_referees}}
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error assigning referee: {e}")
        return {"error": f"An error occurred: {str(e)}"}


def remove_referee(
        manuscript_id: str, referee_email: str) -> Optional[dict]:
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

        dbc.update_doc(
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
