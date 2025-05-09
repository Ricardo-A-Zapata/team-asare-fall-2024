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
EDITOR_EMAIL = 'editor'
REPORT = 'report'
VERDICT = 'verdict'
VERSION = 'version'
REVISIONS = 'revisions'
REVIEW_ROUND = 'review_round'
REFEREE_COMMENTS = 'referee_comments'
AUTHOR_RESPONSE = 'author_response'
TIMESTAMP = 'timestamp'

# Constants for validation
MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 200
MIN_ABSTRACT_LENGTH = 0
MAX_ABSTRACT_LENGTH = 5000

# Constants for manuscript states
STATE_SUBMITTED = 'SUBMITTED'
STATE_ACCEPTED = 'ACCEPTED'
STATE_REJECTED = 'REJECTED'
STATE_COPY_EDIT = 'COPY_EDIT'
STATE_AUTHOR_REVIEW = 'AUTHOR_REVIEW'
STATE_FORMATTING = 'FORMATTING'
STATE_PUBLISHED = 'PUBLISHED'
STATE_WITHDRAWN = 'WITHDRAWN'
STATE_REFEREE_REVIEW = 'REFEREE_REVIEW'
STATE_EDITOR_REVIEW = 'EDITOR_REVIEW'
STATE_AUTHOR_REVISIONS = 'AUTHOR_REVISIONS'

# Action constants for the FSM
ACTION_ASSIGN_REFEREE = 'ASSIGN_REFEREE'
ACTION_REMOVE_REFEREE = 'REMOVE_REFEREE'
ACTION_SUBMIT_REVIEW = 'SUBMIT_REVIEW'
ACTION_ACCEPT = 'ACCEPT'
ACTION_ACCEPT_WITH_REVISIONS = 'ACCEPT_WITH_REVISIONS'
ACTION_REJECT = 'REJECT'
ACTION_DONE = 'DONE'
ACTION_WITHDRAW = 'WITHDRAW'
ACTION_EDITOR_MOVE = 'EDITOR_MOVE'

VALID_STATES = {
    STATE_SUBMITTED,
    STATE_ACCEPTED,
    STATE_REJECTED,
    STATE_COPY_EDIT,
    STATE_AUTHOR_REVIEW,
    STATE_FORMATTING,
    STATE_PUBLISHED,
    STATE_WITHDRAWN,
    STATE_REFEREE_REVIEW,
    STATE_EDITOR_REVIEW,
    STATE_AUTHOR_REVISIONS
}

VERDICT_ACCEPT = 'ACCEPT'
VERDICT_REJECT = 'REJECT'

MANUSCRIPTS_COLLECTION = 'manuscripts'

# Manuscript workflow state machine based on the FSM diagram
MANUSCRIPT_FLOW_MAP = {
    STATE_SUBMITTED: {
        ACTION_ASSIGN_REFEREE: STATE_REFEREE_REVIEW,
        ACTION_REJECT: STATE_REJECTED,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_REFEREE_REVIEW: {
        ACTION_ASSIGN_REFEREE: STATE_REFEREE_REVIEW,
        ACTION_REMOVE_REFEREE: STATE_REFEREE_REVIEW,
        ACTION_SUBMIT_REVIEW: None,
        ACTION_ACCEPT: STATE_COPY_EDIT,
        ACTION_ACCEPT_WITH_REVISIONS: STATE_AUTHOR_REVISIONS,
        ACTION_REJECT: STATE_REJECTED,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_AUTHOR_REVISIONS: {
        ACTION_DONE: STATE_EDITOR_REVIEW,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_EDITOR_REVIEW: {
        ACTION_ACCEPT: STATE_COPY_EDIT,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_COPY_EDIT: {
        ACTION_DONE: STATE_AUTHOR_REVIEW,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_AUTHOR_REVIEW: {
        ACTION_DONE: STATE_FORMATTING,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_FORMATTING: {
        ACTION_DONE: STATE_PUBLISHED,
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_PUBLISHED: {
        ACTION_WITHDRAW: STATE_WITHDRAWN,
        ACTION_EDITOR_MOVE: None,
    },
    STATE_REJECTED: {
        ACTION_EDITOR_MOVE: None,
    },
    STATE_WITHDRAWN: {
        ACTION_EDITOR_MOVE: None,
    },
}

dbc.connect_db()  # connect to MongoDB


def get_collection_name(testing=False):
    """Return the collection name"""
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

    Args:
        title (str): The manuscript title (5-200 characters)
        author (str): The author's name
        author_email (str): The author's email
        text (str): The manuscript text
        abstract (str): The manuscript abstract (100-5000 characters)
        testing (bool): Whether this is a test run

    Raises:
        ValueError: If title or abstract length requirements are not met
    """
    try:
        # Validate title length
        if (len(title.strip()) < MIN_TITLE_LENGTH
                or len(title.strip()) > MAX_TITLE_LENGTH):
            raise ValueError(
                f"Title must be between {MIN_TITLE_LENGTH} and "
                f"{MAX_TITLE_LENGTH} characters"
            )

        # Validate abstract length
        if (len(abstract.strip()) < MIN_ABSTRACT_LENGTH
                or len(abstract.strip()) > MAX_ABSTRACT_LENGTH):
            raise ValueError(
                f"Abstract must be between {MIN_ABSTRACT_LENGTH} and "
                f"{MAX_ABSTRACT_LENGTH} characters"
            )

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
            REFEREES: {},
            TEXT: text,
            ABSTRACT: abstract,
            VERSION: 1,
            REVISIONS: [{
                VERSION: 1,
                TEXT: text,
                ABSTRACT: abstract,
                TIMESTAMP: timestamp,
                REVIEW_ROUND: 0,
                REFEREE_COMMENTS: [],
                AUTHOR_RESPONSE: None
            }],
            HISTORY: [
                {
                    "state": STATE_SUBMITTED,
                    "timestamp": timestamp,
                    "actor": author_email,
                }
            ],
            EDITOR_EMAIL: None,
            "referee_email": None
        }

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
        manuscript = dbc.fetch_one(
            get_collection_name(testing),
            {"_id": ObjectId(manuscript_id)},
            testing=testing
        )
        if manuscript:
            manuscript['_id'] = str(manuscript['_id'])
        return manuscript
    except Exception as e:
        print(f"Error fetching manuscript: {e}")
        return {"error": f"Invalid manuscript ID or not found: {str(e)}"}


def process_manuscript_action(manuscript_id, action, actor_email=None,
                              **kwargs):
    """Central function for processing manuscript state transitions.

    This function implements the finite state machine (FSM) that controls
    the manuscript workflow.

    Args:
        manuscript_id: The ID of the manuscript
        action: The action to perform (must be one of the ACTION_* constants)
        actor_email: Email of the person performing the action
        **kwargs: Additional parameters needed for specific actions

    Returns:
        The updated manuscript or an error dict
    """
    manuscript = get_manuscript(manuscript_id)
    if not manuscript:
        return {"error": "Manuscript not found"}
    current_state = manuscript[STATE]
    next_state = MANUSCRIPT_FLOW_MAP.get(current_state, {}).get(action)

    # Special handling for actions that require logic
    if action == ACTION_SUBMIT_REVIEW:
        verdict = kwargs.get('verdict')
        if verdict == VERDICT_ACCEPT:
            next_state = STATE_COPY_EDIT
        elif verdict == VERDICT_REJECT:
            next_state = STATE_REJECTED
        elif verdict == ACTION_ACCEPT_WITH_REVISIONS:
            next_state = STATE_AUTHOR_REVISIONS
        else:
            return {"error": "Invalid verdict for review submission."}
        # Update referee's report and verdict
        referee_email = kwargs.get('referee_email')
        report = kwargs.get('report', '')
        referees = manuscript.get(REFEREES, {})
        if referee_email:
            referees[referee_email] = {REPORT: report, VERDICT: verdict}
        update_fields = {
            STATE: next_state,
            REFEREES: referees,
            HISTORY: manuscript.get(HISTORY, []) + [{
                "state": next_state,
                "timestamp": datetime.now().isoformat(),
                "actor": referee_email,
                "action": action,
                "verdict": verdict
            }]
        }
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": update_fields}
        )
        return get_manuscript(manuscript_id)
    elif action == ACTION_REMOVE_REFEREE:
        referee_email = kwargs.get('referee_email')
        referees = manuscript.get(REFEREES, {})
        if referee_email in referees:
            del referees[referee_email]
        # If no referees left, return to SUBMITTED
        if not referees:
            next_state = STATE_SUBMITTED
        else:
            next_state = STATE_REFEREE_REVIEW
        update_fields = {
            STATE: next_state,
            REFEREES: referees,
            HISTORY: manuscript.get(HISTORY, []) + [{
                "state": next_state,
                "timestamp": datetime.now().isoformat(),
                "actor": actor_email,
                "action": action
            }]
        }
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": update_fields}
        )
        return get_manuscript(manuscript_id)
    elif action == ACTION_ASSIGN_REFEREE:
        referee_email = kwargs.get('referee_email')
        referees = manuscript.get(REFEREES, {})
        if referee_email and referee_email not in referees:
            referees[referee_email] = {REPORT: '', VERDICT: ''}
        update_fields = {
            STATE: STATE_REFEREE_REVIEW,
            REFEREES: referees,
            HISTORY: manuscript.get(HISTORY, []) + [{
                "state": STATE_REFEREE_REVIEW,
                "timestamp": datetime.now().isoformat(),
                "actor": actor_email,
                "action": action
            }]
        }
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": update_fields}
        )
        return get_manuscript(manuscript_id)
    elif action == ACTION_EDITOR_MOVE:
        target_state = kwargs.get('target_state')
        if target_state not in MANUSCRIPT_FLOW_MAP:
            return {"error": "Invalid target state for editor move."}
        update_fields = {
            STATE: target_state,
            HISTORY: manuscript.get(HISTORY, []) + [{
                "state": target_state,
                "timestamp": datetime.now().isoformat(),
                "actor": actor_email,
                "action": action
            }]
        }
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": update_fields}
        )
        return get_manuscript(manuscript_id)
    elif action == ACTION_WITHDRAW:
        update_fields = {
            STATE: STATE_WITHDRAWN,
            HISTORY: manuscript.get(HISTORY, []) + [{
                "state": STATE_WITHDRAWN,
                "timestamp": datetime.now().isoformat(),
                "actor": actor_email,
                "action": action
            }]
        }
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": update_fields}
        )
        return get_manuscript(manuscript_id)
    # Standard transitions
    if next_state is None:
        return {
            "error": f"Action {action} not allowed from state {current_state}"
        }
    update_fields = {
        STATE: next_state,
        HISTORY: manuscript.get(HISTORY, []) + [{
            "state": next_state,
            "timestamp": datetime.now().isoformat(),
            "actor": actor_email,
            "action": action
        }]
    }
    dbc.update_doc(
        MANUSCRIPTS_COLLECTION,
        {"_id": ObjectId(manuscript_id)},
        {"$set": update_fields}
    )
    return get_manuscript(manuscript_id)


def assign_editor(manuscript_id: str, editor_email: str) -> Optional[dict]:
    """Assign an editor to a manuscript."""
    try:
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            {"$set": {EDITOR_EMAIL: editor_email}}
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
    """Allows an editor to forcefully move a manuscript to any state."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_EDITOR_MOVE,
        actor_email=editor_email,
        target_state=target_state
    )


def author_withdraw(manuscript_id: str, author_email: str) -> Optional[dict]:
    """Allows the author to withdraw a manuscript from any state."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_WITHDRAW,
        actor_email=author_email
    )


def get_referee_verdict(manuscript_id: str) -> Optional[str]:
    """
    returns referee's verdict message.
    """
    manuscript = get_manuscript(manuscript_id)
    if manuscript and "verdict" in manuscript:
        return manuscript["verdict"]
    return None


def reject_manuscript(manuscript_id: str, actor_email: str) -> Optional[dict]:
    """Rejects manuscript using the FSM action handler."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_REJECT,
        actor_email=actor_email
    )


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
    Returns the deleted manuscript if successful,
    or an error message if not found
    """
    try:
        manuscript = get_manuscript(manuscript_id, testing=testing)

        if not manuscript:
            return {"error": "Manuscript not found"}

        if manuscript.get(STATE) == STATE_PUBLISHED:
            return {"error": "Cannot delete a published manuscript"}

        dbc.del_one(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(manuscript_id)},
            db=dbc.JOURNAL_DB,
            testing=testing
        )
        return manuscript

    except Exception as e:
        print(f"Error deleting manuscript: {e}")
        return {"error": f"Invalid manuscript ID or not found: {str(e)}"}


def accept_manuscript(manuscript_id: str, actor_email: str) -> Optional[dict]:
    """Accept a manuscript using the FSM action handler."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_ACCEPT,
        actor_email=actor_email
    )


def accept_with_revisions(
    manuscript_id: str,
    actor_email: str
) -> Optional[dict]:
    """Accept a manuscript with revisions using the FSM action handler."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_ACCEPT_WITH_REVISIONS,
        actor_email=actor_email
    )


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
    """Submit a referee review using the FSM action handler."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_SUBMIT_REVIEW,
        actor_email=referee_email,
        referee_email=referee_email,
        report=report,
        verdict=verdict
    )


def assign_referee(
    manuscript_id: str,
    referee_email: str,
    actor_email: str = None
) -> Optional[dict]:
    """Assign a referee to a manuscript using the FSM action handler."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_ASSIGN_REFEREE,
        actor_email=actor_email or referee_email,
        referee_email=referee_email
    )


def remove_referee(
    manuscript_id: str,
    referee_email: str,
    actor_email: str = None
) -> Optional[dict]:
    """Remove a referee from a manuscript using the FSM action handler."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_REMOVE_REFEREE,
        actor_email=actor_email or referee_email,
        referee_email=referee_email
    )


def submit_author_approval(
    manuscript_id: str,
    author_email: str
) -> Optional[dict]:
    """Author approves changes and moves manuscript to formatting."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_DONE,
        actor_email=author_email
    )


def complete_formatting(
    manuscript_id: str,
    editor_email: str
) -> Optional[dict]:
    """Complete formatting and move to published state."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_DONE,
        actor_email=editor_email
    )


def complete_copy_edit(
    manuscript_id: str,
    editor_email: str
) -> Optional[dict]:
    """Complete copy editing and move to author review."""
    return process_manuscript_action(
        manuscript_id,
        ACTION_DONE,
        actor_email=editor_email
    )


def update_manuscript_text(
    manuscript_id: str,
    new_text: str,
    new_abstract: str,
    author_email: str,
    author_response: str = None,
    testing: bool = False
) -> Optional[dict]:
    """
    Update manuscript text and track the revision.
    """
    try:
        manuscript = get_manuscript(manuscript_id)
        if not manuscript:
            return {"error": "Manuscript not found"}
        current_state = manuscript[STATE]
        if current_state != STATE_SUBMITTED:
            return {
                "error": f"Cannot update manuscript in state: {current_state}"
            }
        timestamp = datetime.now().isoformat()
        current_version = manuscript.get(VERSION, 1)
        new_version = current_version + 1
        new_revision = {
            VERSION: new_version,
            TEXT: new_text,
            ABSTRACT: new_abstract,
            TIMESTAMP: timestamp,
            REVIEW_ROUND: len(manuscript.get(REVISIONS, [])),
            REFEREE_COMMENTS: [],
            AUTHOR_RESPONSE: author_response
        }
        manuscript[TEXT] = new_text
        manuscript[ABSTRACT] = new_abstract
        manuscript[VERSION] = new_version
        manuscript[REVISIONS] = manuscript.get(REVISIONS, []) + [new_revision]
        manuscript[HISTORY].append({
            "state": current_state,
            "timestamp": timestamp,
            "actor": author_email,
            "action": "text_update",
            "version": new_version
        })
        _id = manuscript.pop('_id')
        dbc.update_doc(
            MANUSCRIPTS_COLLECTION,
            {"_id": ObjectId(_id)},
            manuscript
        )
        return get_manuscript(manuscript_id)
    except Exception as e:
        print(f"Error updating manuscript text: {e}")
        return {"error": str(e)}


def get_manuscript_version(
    manuscript_id: str,
    version: int,
    testing: bool = False
) -> Optional[dict]:
    """
    Get a specific version of a manuscript.
    Args:
        manuscript_id: The ID of the manuscript
        version: The version number to retrieve
        testing: Whether this is a test operation
    Returns:
        The manuscript version or None if not found
    """
    try:
        manuscript = get_manuscript(manuscript_id)
        if (
            "error" in manuscript
            or version < 1
            or version > manuscript.get(VERSION, 1)
        ):
            return {"error": f"Version {version} does not exist"}

        revision = next(
            (
                rev for rev in manuscript.get(REVISIONS, [])
                if rev[VERSION] == version
            ),
            None,
        )

        if not revision:
            return {"error": f"Version {version} not found"}

        return {
            TEXT: revision[TEXT],
            ABSTRACT: revision[ABSTRACT],
            VERSION: version,
            "current_version": manuscript[VERSION],
        }

    except Exception as e:
        print(f"Error getting manuscript version: {e}")
        return {"error": f"An error occurred: {str(e)}"}


def get_manuscripts_by_state(state: str, testing=False) -> Dict:
    """
    Retrieve all manuscripts in a specific state.

    Args:
        state (str): The state to filter by (must be one of VALID_STATES)
        testing (bool): Whether this is a test run

    Returns:
        Dict: A dictionary containing the list of manuscripts and count

    Raises:
        ValueError: If the provided state is not valid
    """
    try:
        if state not in VALID_STATES:
            raise ValueError(f"Invalid state. Must be one of: {VALID_STATES}")

        collection = get_collection_name(testing)
        manuscripts = list(dbc.fetch_all(collection, {STATE: state}))

        # Convert ObjectId to string for each manuscript
        for manuscript in manuscripts:
            manuscript['_id'] = str(manuscript['_id'])

        return {
            'manuscripts': manuscripts,
            'count': len(manuscripts)
        }

    except Exception as e:
        print(f"Error fetching manuscripts by state: {e}")
        return {'manuscripts': [], 'count': 0, 'error': str(e)}


def update_state(
    manuscript_id: str,
    state: str,
    editor_email: str
) -> Optional[dict]:
    """
    Update the state of a manuscript directly (for testing purposes).

    Args:
        manuscript_id: The ID of the manuscript
        state: The new state to set
        editor_email: The email of the editor making the change

    Returns:
        The updated manuscript or an error dict
    """
    if state not in VALID_STATES:
        return {"error": f"Invalid state: {state}"}
    return editor_move(manuscript_id, state, editor_email)
