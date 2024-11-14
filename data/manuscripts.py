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
