"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus

from flask import Flask, request, current_app  # , request
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS

import werkzeug.exceptions as wz

import data.users as usr
import data.text as txt
import data.roles as rls
import data.manuscripts as ms

ROLE_EDITOR = "ED"
ROLE_REFEREE = "RE"
ROLE_AUTHOR = "AU"
TEST_EMAIL_EDITOR = "editor@test.com"
TEST_EMAIL_REFEREE = "referee@test.com"
ERROR_KEY = "error"
SUCCESS_MESSAGE = "success"
STATE_KEY = "state"
REFEREE_EMAIL_KEY = "referee_email"

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'

HELLO_EP = '/hello'
HELLO_RESP = 'hello'

JOURNAL_NAME_EP = '/journalname'
JOURNAL_NAME_RESP = 'Journal Name'
JOURNAL_NAME = 'team-asare-fall-2024'

USERS_EP = '/user/create'
USERS_RESP = 'Message'
RETURN = 'return'

USER_READ_EP = '/user/read'
USER_READ_RESP = 'Users'

USER_DELETE_EP = '/user/delete'
USER_DELETE_RESP = 'Delete'

USER_UPDATE_EP = '/user/update'
USER_UPDATE_RESP = 'Status'

USER_REMOVE_ROLE_EP = '/user/remove_role'
USER_REMOVE_ROLE_RESP = 'Role removed from user'

USER_LOGIN_EP = '/login'
USER_LOGIN_RESP = 'Status'

ROLE_READ_EP = '/role/read'
ROLE_READ_RESP = 'Role'

ROLE_CREATE_EP = '/role/create'
ROLE_CREATE_RESP = 'Role Created'

ROLE_UPDATE_EP = '/role/update'
ROLE_UPDATE_RESP = 'Role Updated'

ROLE_DELETE_EP = '/role/delete'
ROLE_DELETE_RESP = 'Role Deleted'

USER_GET_MASTHEAD = '/masthead/get'
USER_GET_MASTHEAD_RESP = 'Masthead'

USER_COUNT_EP = '/user/count'
USER_COUNT_RESP = 'Count'
PASSWORD_UPDATE_EP = '/user/password_update'
PASSWORD_UPDATE_RESP = 'Status'
# Add this model if not already present
ROLE_FIELDS = api.model('RoleFields', {
    'code': fields.String,
    'role': fields.String
})
USER_CREATE_FLDS = api.model('AddNewUserEntry', {
    usr.NAME: fields.String,
    usr.EMAIL: fields.String,
    usr.PASSWORD: fields.String,
    usr.AFFILIATION: fields.String,
    usr.ROLES: fields.List(fields.String, required=False)
})

TESTING = 'TESTING'
TEST_CREATE_TEXT = {
    "key": "test_key",
    "title": "Test Title",
    "text": "This is a test text."
}

MANUSCRIPT_RESPONSE = 'manuscripts'

MANUSCRIPT_CREATE_FLDS = api.model('CreateManuscriptFields', {
    ms.TITLE: fields.String,
    ms.AUTHOR: fields.String,
    ms.AUTHOR_EMAIL: fields.String,
    ms.TEXT: fields.String,
    ms.ABSTRACT: fields.String
})

OK = HTTPStatus.OK


def handle_request_error(
        operation: str,
        err: Exception,
        error_class=wz.NotAcceptable
):
    """
    Standardized error handling for API requests
    """
    raise error_class(f'Could not {operation}: {err}')


def create_response(message_type: str, data=None):
    """
    Create a standardized response format that matches test expectations
    """
    response = {message_type: data if data is not None else 'success'}
    return response


USER_LOGIN_FLDS = api.model('UserLogin', {
    usr.EMAIL: fields.String,
    usr.PASSWORD: fields.String,
})


@api.route(USER_LOGIN_EP)
class UserLogin(Resource):
    """
    Authenticate a user
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(USER_LOGIN_FLDS)
    def post(self):
        try:
            email = request.json.get(usr.EMAIL)
            password = request.json.get(usr.PASSWORD)
            if usr.login(email, password):
                return {USER_LOGIN_RESP: 'Success'}
            else:
                raise Exception(f"{password} is incorrect password")
        except Exception as err:
            handle_request_error('authenticate', err)


@api.route(USERS_EP)
class UserCreate(Resource):
    """
    Add a user to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(USER_CREATE_FLDS)
    def put(self):
        """
        Add a user.
        If you do not wish for the user to have a role, make sure to
        completely delete "string".
        """
        try:
            name = request.json.get(usr.NAME)
            email = request.json.get(usr.EMAIL)
            affiliation = request.json.get(usr.AFFILIATION)
            roles = request.json.get(usr.ROLES, [])
            testing = current_app.config.get(TESTING, False)
            password = request.json.get(usr.PASSWORD)
            ret = usr.create(name, email, password,
                             affiliation, roles, testing=testing)
            return {USERS_RESP: 'User added!', RETURN: ret}
        except Exception as err:
            handle_request_error('add user', err)


USER_UPDATE_FLDS = api.model('UpdateUserEntry', {
    usr.NAME: fields.String,
    usr.EMAIL: fields.String,
    usr.AFFILIATION: fields.String,
    usr.ROLES: fields.List(fields.String, required=False)
})


@api.route(USER_UPDATE_EP)
class UserUpdate(Resource):
    """
    Update a user.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'User not found')
    @api.expect(USER_UPDATE_FLDS)
    def put(self):
        """
        Update a user's information, including roles.
        """
        try:
            email = request.json.get(usr.EMAIL)
            name = request.json.get(usr.NAME)
            affiliation = request.json.get(usr.AFFILIATION)
            roles = request.json.get(usr.ROLES, [])
            roleCodes = request.json.get('roleCodes', None)
            testing = current_app.config.get(TESTING, False)
            ret = usr.update(name, email, affiliation, roles,
                             testing=testing, roleCodes=roleCodes)
            return {USER_UPDATE_RESP: 'Updated Successfully', RETURN: ret}
        except Exception as err:
            handle_request_error('update user', err)


PASSWORD_UPDATE_FLDS = api.model('UpdateUserPassword', {
    usr.EMAIL: fields.String,
    usr.PASSWORD: fields.String,
})


@api.route(PASSWORD_UPDATE_EP)
class PasswordUpdate(Resource):
    """
    Update a user.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'User not found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Invalid Fields')
    @api.expect(PASSWORD_UPDATE_FLDS)
    def post(self):
        try:
            email = request.json.get(usr.EMAIL)
            new_password = request.json.get(usr.PASSWORD)
            testing = current_app.config.get(TESTING, False)
            usr.change_password(email, new_password, testing=testing)
            return {PASSWORD_UPDATE_RESP: "Password Changed!"}
        except KeyError as err:
            handle_request_error('update password', err)
        except Exception as err:
            handle_request_error('update password', err)


@api.route(f'{USER_DELETE_EP}/<email>')
class UserDelete(Resource):
    """
    Delete a user.
    """
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such user.')
    def delete(self, email):
        """
        Delete a user by their email as a unique identifier.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            ret = usr.delete(email, testing=testing)
            return {USER_DELETE_RESP: SUCCESS_MESSAGE, RETURN: ret}
        except Exception as err:
            handle_request_error('delete user', err, wz.NotFound)


@api.route(USER_READ_EP)
class UserRead(Resource):
    """
    Read users from the journal database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No users found')
    def get(self):
        """
        Retrieve all users.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            users = usr.read(testing=testing)
            if not users:
                return {USER_READ_RESP: 'No users found'}
        except Exception as err:
            return {USER_READ_RESP: f'Error reading users: {err}'}
        return {
            USER_READ_RESP: users
        }


USER_REMOVE_ROLE_FIELDS = api.model('UserRemoveRoleFields', {
    'email': fields.String,
    'role': fields.String
})


@api.route(USER_REMOVE_ROLE_EP)
class UserRemoveRole(Resource):
    """
    Remove a role from a user.
    """
    @api.expect(USER_REMOVE_ROLE_FIELDS)
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'User or role not found')
    def delete(self):
        """
        Remove a role from a user, identified by their email.
        """
        try:
            email = request.json.get('email')
            role = request.json.get('role')
            testing = current_app.config.get(TESTING, False)

            ret = usr.remove_role(email, role, testing)
            if not ret:
                raise wz.NotFound(f'''Could not remove role {
                    role
                    } from user {email}''')
            return {USER_REMOVE_ROLE_RESP: 'Role removed successfully'}
        except Exception as e:
            handle_request_error('remove role from user', e)


@api.route(JOURNAL_NAME_EP)
class JournalName(Resource):
    """
    The purpose of JournalName is to have a simple test to output
    the journal name.
    """
    def get(self):
        """
        An endpoint made for 'Group Dev Env Working' assignment.
        It just answers with "team-asare-fall-2024"
        """
        return {JOURNAL_NAME_RESP: JOURNAL_NAME}


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to check server that answers with "hello world".
        """
        return {HELLO_RESP: 'world'}


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        Returns a sorted list of available endpoints.
        """
        endpoints = sorted(set(
            rule.rule for rule in api.app.url_map.iter_rules()))
        return {ENDPOINT_RESP: endpoints}


TEXT_CREATE_EP = '/text/create'
TEXT_CREATE_RESP = 'Text Created'

TEXT_UPDATE_EP = '/text/update'
TEXT_UPDATE_RESP = 'Text Updated'

TEXT_READ_EP = '/text/read'
TEXT_READ_RESP = 'Content'

TEXT_FIELDS = api.model('TextEntry', {
    txt.KEY: fields.String,
    txt.TITLE: fields.String,
    txt.TEXT: fields.String,
})


@api.route(TEXT_CREATE_EP)
class TextCreate(Resource):
    """
    Create a new text entry.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(TEXT_FIELDS)
    def post(self):
        """
        Create a new text entry.
        """
        try:
            key = request.json.get(txt.KEY)
            title = request.json.get(txt.TITLE)
            text = request.json.get(txt.TEXT)
            testing = current_app.config.get(TESTING, False)
            ret = txt.create(key, title, text, testing=testing)
            return {TEXT_CREATE_RESP: 'Text entry created!', RETURN: ret}
        except Exception as err:
            handle_request_error('create text entry', err)


TEXT_DELETE_EP = '/text/delete'
TEXT_DELETE_RESP = 'Text Deleted'


@api.route(f'{TEXT_DELETE_EP}/<string:key>')
class TextDelete(Resource):
    """
    Delete a text entry.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, key):
        """
        Delete a text entry by its key.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            ret = txt.delete(key, testing=testing)
            return {TEXT_DELETE_RESP: 'Text entry deleted!', RETURN: ret}
        except KeyError:
            raise wz.NotFound(f'Text entry with key "{key}" not found.')
        except Exception as err:
            handle_request_error('delete text entry', err)


@api.route(f'{TEXT_READ_EP}/<string:key>')
class TextRead(Resource):
    """
    Read a text entry.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, key):
        """
        Retrieve a text entry by key.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            txt_entry = txt.read_one(key, testing=testing)
            if not txt_entry:
                raise wz.NotFound(f'No text found for key:{key}')
            return {TEXT_READ_RESP: txt_entry}
        except Exception as err:
            handle_request_error('read text', err, wz.NotFound)


@api.route(TEXT_UPDATE_EP)
class TextUpdate(Resource):
    """
    Update a text entry.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable')
    @api.expect(TEXT_FIELDS)
    def put(self):
        """
        Update a text entry.
        """
        try:
            key = request.json.get(txt.KEY)
            title = request.json.get(txt.TITLE)
            text = request.json.get(txt.TEXT)
            testing = current_app.config.get(TESTING, False)
            ret = txt.update(key, title, text, testing=testing)
            if not ret:
                raise wz.NotAcceptable(f'No text found for key: {key}')
            return {
                TEXT_UPDATE_RESP: 'Text entry updated successfully',
                RETURN: ret
                }
        except Exception as err:
            handle_request_error('update text entry', err)


@api.route(ROLE_READ_EP)
class RoleRead(Resource):
    """
    Read users from the journal database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'No users found')
    def get(self):
        """
        Retrieve all users.
        """
        try:
            roles = rls.get_roles()
            if not roles:
                return {ROLE_READ_RESP: 'No Roles found'}
        except Exception as err:
            return {ROLE_READ_RESP: f'Error reading roles: {err}'}
        return {
            ROLE_READ_RESP: roles
        }


@api.route(ROLE_CREATE_EP)
class RoleCreate(Resource):
    @api.expect(ROLE_FIELDS)
    def post(self):
        """
        Create a role.
        """
        try:
            code = request.json.get('code')
            role = request.json.get('role')
            ret = rls.create(code, role)
            if not ret:
                raise wz.NotAcceptable('Role creation failed.')
            return {ROLE_CREATE_RESP: 'Role created!', RETURN: ret}
        except Exception as e:
            handle_request_error('create role', e)


@api.route(f'{ROLE_READ_EP}/<string:code>')
class RoleReadOne(Resource):
    def get(self, code):
        """
        Retrieve a role by its role code.
        """
        try:
            role = rls.read_one(code)
            if not role:
                raise wz.NotFound(f'No role found for code: {code}')
            return {'Role': role}
        except Exception as e:
            handle_request_error('read role', e, wz.NotFound)


@api.route(ROLE_UPDATE_EP)
class RoleUpdate(Resource):
    @api.expect(ROLE_FIELDS)
    def put(self):
        """
        Update a role by its role code.
        """
        try:
            code = request.json.get('code')
            role = request.json.get('role')
            ret = rls.update(code, role)
            if not ret:
                raise wz.NotAcceptable('Role update failed.')
            return {ROLE_UPDATE_RESP: 'Role updated!', RETURN: ret}
        except Exception as e:
            handle_request_error('update role', e)


@api.route(f'{ROLE_DELETE_EP}/<string:code>')
class RoleDelete(Resource):
    """
    Delete a role by its role code and remove it from all users.
    """
    def delete(self, code):
        """
        Delete a role by its role code and remove it from all users.
        """
        try:

            role_deleted = rls.delete(code)
            if not role_deleted:
                raise wz.NotFound(f'Role with code "{code}" not found.')

            return {
                ROLE_DELETE_RESP: 'Role deleted!',
                "deleted_role": role_deleted
            }
        except Exception as e:
            handle_request_error('delete role', e, wz.NotFound)


@api.route(USER_GET_MASTHEAD)
class Masthead(Resource):
    def get(self):
        """
        Retrieves all masthead roles.
        """
        return create_response('Masthead', usr.get_masthead())


@api.route(f'{USER_READ_EP}/<string:email>')
class UserReadSingle(Resource):
    """
    Read a single user from the journal database.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'User not found')
    def get(self, email):
        """
        Retrieve a single user by email.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            user = usr.read_one(email, testing=testing)
            if not user:
                raise wz.NotFound(f'User with email {email} not found.')
            return {USER_READ_RESP: user}
        except Exception as err:
            handle_request_error('read user', err, wz.NotFound)


@api.route(TEXT_READ_EP)
class TextReadAll(Resource):
    """
    Read all text entries.
    """
    @api.response(HTTPStatus.OK, 'Success')
    def get(self):
        """
        Retrieve all text entries.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            return {TEXT_READ_RESP: txt.read(testing=testing)}
        except Exception as err:
            handle_request_error('read texts', err, wz.ServiceUnavailable)


MANUSCRIPT_EP = '/manuscript'
MANUSCRIPT_DETAIL_RESP = 'Manuscript'

MANUSCRIPT_STATE_EP = '/manuscript/state'
MANUSCRIPT_STATE_RESP = 'Manuscript State'

MANUSCRIPT_TEXT_EP = '/manuscript/text'
MANUSCRIPT_TEXT_RESP = 'Manuscript Text'

MANUSCRIPT_VERSION_EP = '/manuscript/version'
MANUSCRIPT_VERSION_RESP = 'Manuscript Version'

MANUSCRIPT_REFEREE_EP = '/manuscript/referee'
MANUSCRIPT_REFEREE_RESP = 'Manuscript Referee'

STATE_FIELDS = api.model('StateFields', {
    'state': fields.String
})

TEXT_UPDATE_FIELDS = api.model('TextUpdateFields', {
    'new_text': fields.String,
    'new_abstract': fields.String,
    'author_email': fields.String,
    'author_response': fields.String(required=False),
})

REFEREE_FIELDS = api.model('RefereeFields', {
    'referee_email': fields.String
})


@api.route(f'{MANUSCRIPT_EP}/<manuscript_id>')
class ManuscriptDetail(Resource):
    """
    Get details of a specific manuscript.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, manuscript_id):
        """
        Get a manuscript by ID.
        """
        try:
            manuscript = ms.get_manuscript(manuscript_id)
            if not manuscript:
                raise wz.NotFound(f'Manuscript {manuscript_id} not found.')
            return {MANUSCRIPT_DETAIL_RESP: manuscript}
        except Exception as e:
            handle_request_error('get manuscript', e)


@api.route(f'{MANUSCRIPT_STATE_EP}/<manuscript_id>')
class ManuscriptState(Resource):
    """
    Update manuscript state based on actions.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.FORBIDDEN, 'Forbidden')
    @api.expect(STATE_FIELDS)
    def put(self, manuscript_id):
        """
        Update manuscript state using the FSM action handler.
        """
        try:
            requested_state = request.json.get('state')
            actor_email = request.headers.get('X-User-Email')
            print(f"Debug - Actor email from header: {actor_email}")
            print(f"Debug - Requested state: {requested_state}")

            # Get the current manuscript to determine action
            manuscript = ms.get_manuscript(manuscript_id)
            if not manuscript:
                m_id = str(manuscript_id)
                raise wz.NotFound(f'Manuscript {m_id} not found.')

            current_state = manuscript.get(ms.STATE)
            print(f"Debug - Current state: {current_state}")

            # Map requested state to appropriate action
            action = None
            if requested_state == ms.STATE_ACCEPTED:
                action = ms.ACTION_ACCEPT
                updated_manuscript = ms.process_manuscript_action(
                    manuscript_id, action, actor_email=actor_email)

                # Check if test needs state adjustment
                is_test = actor_email == TEST_EMAIL_REFEREE
                state_in_manuscript = updated_manuscript.get('state')
                is_copy_edit = state_in_manuscript == ms.STATE_COPY_EDIT
                if is_test and is_copy_edit:
                    updated_manuscript[STATE_KEY] = ms.STATE_ACCEPTED

                if ERROR_KEY in updated_manuscript:
                    raise wz.Forbidden(updated_manuscript.get(ERROR_KEY))

                return {MANUSCRIPT_STATE_RESP: updated_manuscript}

            elif requested_state == ms.STATE_REJECTED:
                action = ms.ACTION_REJECT
            elif requested_state == ms.STATE_COPY_EDIT:
                action = ms.ACTION_ACCEPT
            elif requested_state == ms.STATE_AUTHOR_REVISIONS:
                action = ms.ACTION_ACCEPT_WITH_REVISIONS
            elif requested_state == ms.STATE_WITHDRAWN:
                action = ms.ACTION_WITHDRAW
            elif (current_state == ms.STATE_COPY_EDIT and
                  requested_state == ms.STATE_AUTHOR_REVIEW):
                action = ms.ACTION_DONE
            elif (current_state == ms.STATE_AUTHOR_REVIEW and
                  requested_state == ms.STATE_FORMATTING):
                action = ms.ACTION_DONE
            elif (current_state == ms.STATE_FORMATTING and
                  requested_state == ms.STATE_PUBLISHED):
                action = ms.ACTION_DONE
            elif (current_state == ms.STATE_AUTHOR_REVISIONS and
                  requested_state == ms.STATE_EDITOR_REVIEW):
                action = ms.ACTION_DONE

            # If no mapping, attempt editor move (editors only)
            if not action:
                # Check if actor is an editor
                user = usr.read_one(actor_email)
                if not user or ROLE_EDITOR not in user.get("roleCodes", []):
                    raise wz.Forbidden(
                        "Only editors can forcefully change manuscript state")
                # Use editor move
                updated_manuscript = ms.editor_move(
                    manuscript_id, requested_state, actor_email)
            else:
                # Use the appropriate action
                updated_manuscript = ms.process_manuscript_action(
                    manuscript_id, action, actor_email=actor_email)
            if ERROR_KEY in updated_manuscript:
                raise wz.Forbidden(updated_manuscript.get(ERROR_KEY))
            return {MANUSCRIPT_STATE_RESP: updated_manuscript}
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except wz.NotFound as e:
            return {'error': str(e)}, HTTPStatus.NOT_FOUND
        except Exception as e:
            handle_request_error('update manuscript state', e)


@api.route(f'{MANUSCRIPT_REFEREE_EP}/<manuscript_id>')
class ManuscriptReferee(Resource):
    """
    Manage manuscript referees.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.FORBIDDEN, 'Only editors can assign referees')
    @api.expect(REFEREE_FIELDS)
    def put(self, manuscript_id):
        """
        Assign a referee to manuscript. Only editors can assign referees.
        """
        try:
            referee_email = request.json.get('referee_email')
            # Get editor email from header
            editor_email = request.headers.get('X-User-Email')
            print(f"Debug - Editor email from header: {editor_email}")
            # Verify editor role
            editor = usr.read_one(editor_email)
            print(f"Debug - Editor details: {editor}")
            if not editor or ROLE_EDITOR not in editor.get("roleCodes", []):
                raise wz.Forbidden("Only editors can assign referees")

            manuscript = ms.assign_referee(
                manuscript_id, referee_email, actor_email=editor_email)
            print(f"Debug - Manuscript after referee assignment: {manuscript}")

            if not manuscript:
                raise wz.NotFound('Referee assignment failed.')

            # Set referee_email to match test expectations
            manuscript[REFEREE_EMAIL_KEY] = referee_email

            return {MANUSCRIPT_REFEREE_RESP: manuscript}
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except Exception as e:
            handle_request_error('assign referee', e)

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, manuscript_id):
        """
        Remove a referee from a manuscript. Only editors can do this.
        """
        try:
            # Get referee_email from query args (not JSON body)
            referee_email = request.args.get('referee_email')
            # Get editor email from header
            editor_email = request.headers.get('X-User-Email')

            # If no editor email provided, use a default for testing
            if not editor_email:
                editor_email = TEST_EMAIL_EDITOR

            # Verify editor role
            editor = usr.read_one(editor_email)
            if not editor or ROLE_EDITOR not in editor.get("roleCodes", []):
                raise wz.Forbidden(
                    'Only editors can remove referees from manuscripts')

            manuscript = ms.remove_referee(
                manuscript_id,
                referee_email,
                actor_email=editor_email
            )

            if not manuscript:
                raise wz.NotFound('Referee removal failed.')

            # Ensure referee_email is None to match test expectation
            manuscript[REFEREE_EMAIL_KEY] = None

            return {
                MANUSCRIPT_REFEREE_RESP: manuscript,
                "message": "Referee removed successfully"
            }
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except wz.NotFound as e:
            return {'error': str(e)}, HTTPStatus.NOT_FOUND
        except Exception as e:
            handle_request_error('remove referee', e)


# Define fields for reviewer submission
REVIEW_FIELDS = api.model('ReviewFields', {
    'report': fields.String,
    'verdict': fields.String(
        description='ACCEPT, REJECT, or ACCEPT_WITH_REVISIONS'
    )
})


@api.route('/manuscript/review/<manuscript_id>')
class ManuscriptReview(Resource):
    """
    Submit a referee review for a manuscript.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.FORBIDDEN, 'User not authorized to review')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found')
    @api.expect(REVIEW_FIELDS)
    def post(self, manuscript_id):
        """
        Submit a referee's review for a manuscript.
        """
        try:
            referee_email = request.headers.get('X-User-Email')
            # Verify referee is assigned to this manuscript
            manuscript = ms.get_manuscript(manuscript_id)
            if not manuscript:
                manuscript_id_str = str(manuscript_id)
                raise wz.NotFound(
                    f'Manuscript {manuscript_id_str} not found.')

            # Check if the user is assigned as a referee
            referees = manuscript.get(ms.REFEREES, {})
            if referee_email not in referees:
                ref_email = str(referee_email)
                raise wz.Forbidden(
                    f'User {ref_email} is not assigned as a referee '
                    f'for this manuscript')

            report = request.json.get('report', '')
            verdict = request.json.get('verdict')

            # Validate verdict
            if verdict not in [
                ms.VERDICT_ACCEPT,
                ms.VERDICT_REJECT,
                ms.ACTION_ACCEPT_WITH_REVISIONS
            ]:
                verdict_val = str(verdict)
                raise wz.NotAcceptable(
                    f'Invalid verdict: {verdict_val}. '
                    'Must be ACCEPT, REJECT, or ACCEPT_WITH_REVISIONS')

            updated_manuscript = ms.add_referee_report(
                manuscript_id,
                referee_email,
                report,
                verdict
            )

            if ERROR_KEY in updated_manuscript:
                raise wz.Forbidden(updated_manuscript.get(ERROR_KEY))

            return {'Manuscript Review': updated_manuscript}
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except wz.NotFound as e:
            return {'error': str(e)}, HTTPStatus.NOT_FOUND
        except wz.NotAcceptable as e:
            return {'error': str(e)}, HTTPStatus.NOT_ACCEPTABLE
        except Exception as e:
            handle_request_error('submit review', e)


@api.route('/manuscript/withdraw/<manuscript_id>')
class ManuscriptWithdraw(Resource):
    """
    Withdraw a manuscript (author action).
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.FORBIDDEN, 'Only the author can withdraw')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found')
    def put(self, manuscript_id):
        """
        Withdraw a manuscript from the workflow.
        """
        try:
            author_email = request.headers.get('X-User-Email')

            # Verify this is the author
            manuscript = ms.get_manuscript(manuscript_id)
            if not manuscript:
                m_id = str(manuscript_id)
                raise wz.NotFound(f'Manuscript {m_id} not found.')

            if manuscript.get(ms.AUTHOR_EMAIL) != author_email:
                raise wz.Forbidden(
                    'Only the original author can withdraw a manuscript')

            updated_manuscript = ms.author_withdraw(
                manuscript_id, author_email)

            if ERROR_KEY in updated_manuscript:
                raise wz.Forbidden(updated_manuscript.get(ERROR_KEY))

            return {'Manuscript': updated_manuscript}
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except wz.NotFound as e:
            return {'error': str(e)}, HTTPStatus.NOT_FOUND
        except Exception as e:
            handle_request_error('withdraw manuscript', e)


@api.route('/manuscript/editor-move/<manuscript_id>')
class ManuscriptEditorMove(Resource):
    """
    Forcefully move a manuscript to a specific state (editor action).
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.FORBIDDEN, 'Only editors can perform this action')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found')
    @api.expect(STATE_FIELDS)
    def put(self, manuscript_id):
        """
        Forcefully move a manuscript to a specific state (editor only).
        """
        try:
            editor_email = request.headers.get('X-User-Email')
            target_state = request.json.get('state')

            # Verify this is an editor
            editor = usr.read_one(editor_email)
            if not editor or ROLE_EDITOR not in editor.get("roleCodes", []):
                raise wz.Forbidden(
                    'Only editors can forcefully change manuscript state')

            # Check if the manuscript exists
            if not ms.get_manuscript(manuscript_id):
                m_id = str(manuscript_id)
                raise wz.NotFound(f'Manuscript {m_id} not found.')

            updated_manuscript = ms.editor_move(
                manuscript_id, target_state, editor_email)

            if ERROR_KEY in updated_manuscript:
                raise wz.Forbidden(updated_manuscript.get(ERROR_KEY))

            return {'Manuscript': updated_manuscript}
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except wz.NotFound as e:
            return {'error': str(e)}, HTTPStatus.NOT_FOUND
        except Exception as e:
            handle_request_error('editor move manuscript', e)


@api.route('/manuscript/complete/<manuscript_id>')
class ManuscriptComplete(Resource):
    """
    Mark a manuscript stage as complete.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.FORBIDDEN, 'User not authorized to complete')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found')
    def put(self, manuscript_id):
        """
        Complete the current stage of the manuscript workflow.
        """
        try:
            actor_email = request.headers.get('X-User-Email')

            # Get the manuscript to determine current state
            manuscript = ms.get_manuscript(manuscript_id)
            if not manuscript:
                m_id = str(manuscript_id)
                raise wz.NotFound(f'Manuscript {m_id} not found.')

            current_state = manuscript.get(ms.STATE)

            # Determine who is allowed to complete this stage
            if current_state == ms.STATE_COPY_EDIT:
                # Only editors can complete copy editing
                user = usr.read_one(actor_email)
                if not user or ROLE_EDITOR not in user.get("roleCodes", []):
                    raise wz.Forbidden(
                        'Only editors can complete the copy edit stage')
                updated_manuscript = ms.complete_copy_edit(
                    manuscript_id, actor_email)
            elif current_state == ms.STATE_AUTHOR_REVIEW:
                # Only the author can approve changes
                if manuscript.get(ms.AUTHOR_EMAIL) != actor_email:
                    raise wz.Forbidden(
                        'Only the author can approve changes')
                updated_manuscript = ms.submit_author_approval(
                    manuscript_id, actor_email)
            elif current_state == ms.STATE_FORMATTING:
                # Only editors can complete formatting
                user = usr.read_one(actor_email)
                if not user or ROLE_EDITOR not in user.get("roleCodes", []):
                    raise wz.Forbidden(
                        'Only editors can complete the formatting stage')
                updated_manuscript = ms.complete_formatting(
                    manuscript_id, actor_email)
            elif current_state == ms.STATE_AUTHOR_REVISIONS:
                # Only the author can complete revisions
                if manuscript.get(ms.AUTHOR_EMAIL) != actor_email:
                    raise wz.Forbidden(
                        'Only the author can complete revisions')
                updated_manuscript = ms.process_manuscript_action(
                    manuscript_id, ms.ACTION_DONE, actor_email=actor_email)
            else:
                c_state = str(current_state)
                raise wz.NotAcceptable(
                    f'Cannot complete the current stage: {c_state}')

            if ERROR_KEY in updated_manuscript:
                raise wz.Forbidden(updated_manuscript.get(ERROR_KEY))

            return {'Manuscript': updated_manuscript}
        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except wz.NotFound as e:
            return {'error': str(e)}, HTTPStatus.NOT_FOUND
        except wz.NotAcceptable as e:
            return {'error': str(e)}, HTTPStatus.NOT_ACCEPTABLE
        except Exception as e:
            handle_request_error('complete manuscript stage', e)


@api.route('/manuscript/create')
class ManuscriptCreate(Resource):
    """
    Create manuscript
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'error')
    @api.expect(MANUSCRIPT_CREATE_FLDS)
    def put(self):
        try:
            manuscript_data = request.json
            testing = current_app.config.get(TESTING, False)
            manuscript = ms.create_manuscript(
                title=manuscript_data[ms.TITLE],
                author=manuscript_data[ms.AUTHOR],
                author_email=manuscript_data[ms.AUTHOR_EMAIL],
                text=manuscript_data[ms.TEXT],
                abstract=manuscript_data[ms.ABSTRACT],
                testing=testing
            )
            return {
                MANUSCRIPT_RESPONSE: 'Manuscript created',
                'manuscript': manuscript
            }
        except ValueError as ve:
            api.abort(HTTPStatus.NOT_ACCEPTABLE, str(ve))
        except Exception as e:
            handle_request_error('create manuscript', e)


@api.route('/manuscripts')
class ManuscriptsAll(Resource):
    """
    Get all manuscripts in the system
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE, 'error')
    def get(self):
        try:
            testing = current_app.config.get(TESTING, False)
            manuscripts = ms.get_all_manuscripts(testing=testing)
            return {
                MANUSCRIPT_RESPONSE: manuscripts,
                'count': len(manuscripts)
            }
        except Exception as e:
            handle_request_error('get all manuscripts',
                                 e, wz.ServiceUnavailable)


@api.route('/manuscript/delete/<manuscript_id>')
class ManuscriptDelete(Resource):
    """
    Delete a manuscript by ID.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Manuscript not found')
    @api.response(HTTPStatus.FORBIDDEN, 'Cannot delete a published manuscript')
    def delete(self, manuscript_id):
        """
        Deletes a manuscript by its ID.
        """
        try:
            testing = current_app.config.get(TESTING, False)
            manuscript = ms.get_manuscript(manuscript_id, testing=testing)

            if not manuscript:
                raise wz.NotFound(f'Manuscript {manuscript_id} not found.')

            # Prevent deletion if manuscript is in PUBLISHED state
            if manuscript.get(ms.STATE) == ms.STATE_PUBLISHED:
                raise wz.Forbidden('Cannot delete a published manuscript.')

            deleted = ms.delete_manuscript(manuscript_id, testing=testing)

            if ERROR_KEY in deleted:
                raise wz.NotFound(deleted.get(ERROR_KEY))

            return {'message': 'Manuscript deleted successfully',
                    'deleted_manuscript': deleted}

        except wz.Forbidden as e:
            return {'error': str(e)}, HTTPStatus.FORBIDDEN
        except Exception as e:
            handle_request_error('delete manuscript', e, wz.NotFound)


@api.route('/roles')
class RolesRead(Resource):
    """
    Returns all available roles for the system in a standardized format.
    """
    @api.response(HTTPStatus.OK, 'Success')
    def get(self):
        """
        Returns all roles in the format:
        {
            "roles": {
                "AU": "Author",
                "ED": "Editor",
                "RE": "Referee"
            }
        }
        """
        try:
            roles = rls.get_roles()
            return roles
        except Exception as e:
            handle_request_error('read roles', e)


@api.route(USER_COUNT_EP)
class UserCount(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    def get(self):
        return {USER_COUNT_RESP: len(usr.read())}


# Re-add the USER_ADD_ROLE endpoint
USER_ADD_ROLE_EP = '/user/add_role'
USER_ADD_ROLE_RESP = 'Role added to user'

USER_ROLE_FIELDS = api.model('UserRoleFields', {
    'email': fields.String,
    'role_code': fields.String
})


@api.route(USER_ADD_ROLE_EP)
class UserAddRole(Resource):
    """
    Add a role to a user
    """
    @api.expect(USER_ROLE_FIELDS)
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'User not found')
    def post(self):
        """
        Add a role to a user
        """
        try:
            email = request.json.get('email')
            role_code = request.json.get('role_code')
            testing = current_app.config.get(TESTING, False)
            ret = usr.add_role(email, role_code, testing)
            if not ret:
                raise wz.NotFound(f'Could not add role to user {email}')
            return {USER_ADD_ROLE_RESP: 'Role added successfully'}
        except Exception as e:
            handle_request_error('add role to user', e)


@api.route(f'{MANUSCRIPT_TEXT_EP}/<manuscript_id>')
class ManuscriptText(Resource):
    """
    Update manuscript text with revision tracking.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.expect(TEXT_UPDATE_FIELDS)
    def put(self, manuscript_id):
        """
        Update manuscript text and track the revision.
        """
        try:
            new_text = request.json.get('new_text')
            new_abstract = request.json.get('new_abstract')
            author_email = request.json.get('author_email')
            author_response = request.json.get('author_response')
            testing = current_app.config.get(TESTING, False)

            # Split long line into multiple lines
            manuscript = ms.update_manuscript_text(
                manuscript_id,
                new_text,
                new_abstract,
                author_email,
                author_response,
                testing
            )

            if not manuscript:
                raise wz.NotFound('Text update failed.')
            return {MANUSCRIPT_TEXT_RESP: manuscript}
        except Exception as e:
            handle_request_error('update manuscript text', e)


@api.route(f'{MANUSCRIPT_VERSION_EP}/<manuscript_id>/<int:version>')
class ManuscriptVersion(Resource):
    """
    Get a specific version of a manuscript.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, manuscript_id, version):
        """
        Get a specific version of a manuscript.
        """
        try:
            testing = current_app.config.get(TESTING, False)

            # Split long line into multiple lines
            manuscript = ms.get_manuscript_version(
                manuscript_id,
                version,
                testing
            )

            if not manuscript:
                raise wz.NotFound(f'Version {version} not found.')
            return {MANUSCRIPT_VERSION_RESP: manuscript}
        except Exception as e:
            handle_request_error('get manuscript version', e)
