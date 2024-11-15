"""
This file contains the manuscript data and operations.
"""

from typing import Dict, Optional
from datetime import datetime

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

# Constants for manuscript states
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

# Constants for referee verdicts
VERDICT_ACCEPT = 'ACCEPT'
VERDICT_ACCEPT_WITH_REVISIONS = 'ACCEPT_W_REV'
VERDICT_REJECT = 'REJECT'

# In-memory storage (will be replaced with MongoDB)
manuscripts: Dict = {}


def create_manuscript(
    title: str,
    author: str,
    author_email: str,
    text: str,
    abstract: str
) -> dict:
    """
    Create a new manuscript entry.
    """
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
    # For now, use timestamp as ID (will be replaced with MongoDB _id)
    manuscripts[timestamp] = manuscript
    return manuscript


def get_manuscript(manuscript_id: str) -> Optional[dict]:
    """
    Retrieve a manuscript by ID.
    """
    return manuscripts.get(manuscript_id)


def update_state(
    manuscript_id: str,
    new_state: str,
    actor_email: str
) -> Optional[dict]:
    """
    Update the state of a manuscript and record in history.
    """
    manuscript = manuscripts.get(manuscript_id)
    if not manuscript:
        return None
    manuscript[STATE] = new_state
    manuscript[HISTORY].append({
        'state': new_state,
        'timestamp': datetime.now().isoformat(),
        'actor': actor_email
    })
    return manuscript


def assign_referee(
    manuscript_id: str,
    referee_email: str
) -> Optional[dict]:
    """
    Assign a referee to a manuscript.
    """
    manuscript = manuscripts.get(manuscript_id)
    if not manuscript:
        return None
    if referee_email not in manuscript[REFEREES]:
        manuscript[REFEREES][referee_email] = {
            'report': None,
            'verdict': None
        }
    return manuscript


def remove_referee(manuscript_id: str, referee_email: str) -> Optional[dict]:
    manuscript = manuscripts.get(manuscript_id)
    if not manuscript or referee_email not in manuscript[REFEREES]:
        return None
    manuscript[REFEREES].pop(referee_email)
    return manuscript


def submit_review(
    manuscript_id: str,
    referee_email: str,
    report: str,
    verdict: str
) -> Optional[dict]:
    """
    Submit a referee review.
    """
    manuscript = manuscripts.get(manuscript_id)
    if not manuscript or referee_email not in manuscript[REFEREES]:
        return None
    if verdict not in [
        VERDICT_ACCEPT,
        VERDICT_ACCEPT_WITH_REVISIONS,
        VERDICT_REJECT
    ]:
        raise ValueError(f"Invalid verdict: {verdict}")
    manuscript[REFEREES][referee_email].update({
        'report': report,
        'verdict': verdict
    })
    return manuscript


def assign_editor(
    manuscript_id: str,
    editor_email: str
) -> Optional[dict]:
    """
    Assign an editor to a manuscript.
    """
    manuscript = manuscripts.get(manuscript_id)
    if not manuscript:
        return None
    manuscript[EDITOR] = editor_email
    return manuscript


def editor_move(manuscript_id: str, target_state: str, editor_email: str
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
    manuscript = manuscripts.get(manuscript_id)
    if manuscript and "verdict" in manuscript:
        return manuscript["verdict"]
    else:
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


def get_all_manuscripts() -> Dict:
    """
    Get all manuscripts.
    """
    return manuscripts


def delete_manuscript(manuscript_id: str) -> Optional[dict]:
    """
    Delete a manuscript by ID.
    Returns the deleted manuscript if successful, None if not found.
    """
    return manuscripts.pop(manuscript_id, None)


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


def accept_with_revisions(manuscript_id: str, actor_email: str) -> \
Optional[dict]:
    """
    Move manuscript to AUTHOR_REVISIONS after review.
    """
    return update_state(manuscript_id, STATE_AUTHOR_REVISIONS, actor_email)
