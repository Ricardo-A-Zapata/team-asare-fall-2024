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

ROLE_READ_EP = '/role/read'
ROLE_READ_RESP = 'Roles'

ROLE_CREATE_EP = '/role/create'
ROLE_CREATE_RESP = 'Role Created'

ROLE_UPDATE_EP = '/role/update'
ROLE_UPDATE_RESP = 'Role Updated'

ROLE_DELETE_EP = '/role/delete'
ROLE_DELETE_RESP = 'Role Deleted'

USER_GET_MASTHEAD = '/masthead/get'
USER_GET_MASTHEAD_RESP = 'Masthead'

# Add this model if not already present
ROLE_FIELDS = api.model('RoleFields', {
    'code': fields.String,
    'role': fields.String
})
USER_CREATE_FLDS = api.model('AddNewUserEntry', {
    usr.NAME: fields.String,
    usr.EMAIL: fields.String,
    usr.AFFILIATION: fields.String,
    usr.ROLES: fields.List(fields.String, required=False)
})

TESTING = 'TESTING'
TEST_CREATE_TEXT = {
    "key": "test_key",
    "title": "Test Title",
    "text": "This is a test text."
}

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
        """
        try:
            name = request.json.get(usr.NAME)
            email = request.json.get(usr.EMAIL)
            affiliation = request.json.get(usr.AFFILIATION)
            roles = request.json.get(usr.ROLES, [])
            testing = current_app.config.get(TESTING, False)
            ret = usr.create(name, email, affiliation, roles, testing=testing)
            return {USERS_RESP: 'User added!', RETURN: ret}
        except Exception as err:
            handle_request_error('add user', err)


# Add this model for user updates
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
            testing = current_app.config.get(TESTING, False)
            ret = usr.update(name, email, affiliation, roles, testing=testing)
            return {USER_UPDATE_RESP: 'Updated Successfully', RETURN: ret}
        except Exception as err:
            handle_request_error('update user', err)


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
            return {USER_DELETE_RESP: 'success', RETURN: ret}
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

            # Call a function in `users.py` to handle this
            ret = usr.remove_role(email, role, testing)
            if not ret:
                raise wz.NotFound(f'Could not remove role {
                    role
                    } from user {email}')
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
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
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
        The `get()` method will return sorted a list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
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
        try:
            code = request.json['code']
            role = request.json['role']
            ret = rls.create(code, role)
            if not ret:
                raise wz.NotAcceptable('Role creation failed.')
            return {ROLE_CREATE_RESP: 'Role created!', RETURN: ret}
        except Exception as e:
            handle_request_error('create role', e)


@api.route(f'{ROLE_READ_EP}/<string:code>')
class RoleReadOne(Resource):
    def get(self, code):
        try:
            role = rls.read_one(code)
            if not role:
                raise wz.NotFound(f'No role found for code: {code}')
            return {ROLE_READ_RESP: role}
        except Exception as e:
            handle_request_error('read role', e, wz.NotFound)


@api.route(ROLE_UPDATE_EP)
class RoleUpdate(Resource):
    @api.expect(ROLE_FIELDS)
    def put(self):
        try:
            code = request.json['code']
            role = request.json['role']
            ret = rls.update(code, role)
            if not ret:
                raise wz.NotAcceptable('Role update failed.')
            return {ROLE_UPDATE_RESP: 'Role updated!', RETURN: ret}
        except Exception as e:
            handle_request_error('update role', e)


@api.route(f'{ROLE_DELETE_EP}/<string:code>')
class RoleDelete(Resource):
    def delete(self, code):
        try:
            ret = rls.delete(code)
            if not ret:
                raise wz.NotFound(f'Role with code "{code}" not found.')
            return {ROLE_DELETE_RESP: 'Role deleted!', RETURN: ret}
        except Exception as e:
            handle_request_error('delete role', e, wz.NotFound)


@api.route(USER_GET_MASTHEAD)
class Masthead(Resource):
    def get(self):
        return create_response('Masthead', usr.get_masthead())


USER_READ_SINGLE_EP = '/user/read_single'


@api.route(f'{USER_READ_SINGLE_EP}/<string:email>')
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


TEXT_READ_ALL_EP = '/text/read_all'


@api.route(TEXT_READ_ALL_EP)
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

MANUSCRIPT_REFEREE_EP = '/manuscript/referee'
MANUSCRIPT_REFEREE_RESP = 'Manuscript Referee'

STATE_FIELDS = api.model('StateFields', {
    'state': fields.String,
    'actor_email': fields.String,
})

REFEREE_FIELDS = api.model('RefereeFields', {
    'referee_email': fields.String,
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
    Update manuscript state.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.expect(STATE_FIELDS)
    def put(self, manuscript_id):
        """
        Update manuscript state.
        """
        try:
            new_state = request.json.get('state')
            actor_email = request.json.get('actor_email')
            manuscript = ms.update_state(manuscript_id, new_state, actor_email)
            if not manuscript:
                raise wz.NotFound('State update failed.')
            return {MANUSCRIPT_STATE_RESP: manuscript}
        except Exception as e:
            handle_request_error('update manuscript state', e)


@api.route(f'{MANUSCRIPT_REFEREE_EP}/<manuscript_id>')
class ManuscriptReferee(Resource):
    """
    Manage manuscript referees.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.expect(REFEREE_FIELDS)
    def put(self, manuscript_id):
        """
        Assign a referee to manuscript.
        """
        try:
            referee_email = request.json.get('referee_email')
            manuscript = ms.assign_referee(manuscript_id, referee_email)
            if not manuscript:
                raise wz.NotFound('Referee assignment failed.')
            return {MANUSCRIPT_REFEREE_RESP: manuscript}
        except Exception as e:
            handle_request_error('assign referee', e)

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, manuscript_id):
        """
        Remove referee from manuscript.
        """
        try:
            referee_email = request.args.get('referee_email')
            manuscript = ms.remove_referee(manuscript_id, referee_email)
            if not manuscript:
                raise wz.NotFound('Referee removal failed.')
            return {MANUSCRIPT_REFEREE_RESP: manuscript}
        except Exception as e:
            handle_request_error('remove referee', e)


USER_ADD_ROLE_EP = '/user/add_role'
USER_ADD_ROLE_RESP = 'Role added to user'

ROLE_FIELDS = api.model('RoleFields', {
    'code': fields.String,
    'role': fields.String
})

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
