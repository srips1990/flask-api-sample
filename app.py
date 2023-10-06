from flask import Flask, make_response
from flask_restful import Api, Resource, request
from flask_jwt_extended import create_access_token, get_jwt_identity, get_current_user, JWTManager, jwt_required
import sqlite3
from exptns import AuthenticationError, UserDoesNotExistError

# Press the green button in the gutter to run the script.
app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this "super secret" with something else!
jwt = JWTManager(app)
api = Api(app)


class HelloWorld(Resource):

    def post(self, name=''):
        data = 'Hello ' + ('World!' if name == '' else name)
        return {'data': data}


class Login(Resource):

    def post(self):
        try:
            data = request.get_json()
            if 'id' not in data:
                raise UserDoesNotExistError()
            uid = data['id']
            conn = sqlite3.connect('usersdb')
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM users WHERE id = ?', (uid,))
            res = cur.fetchone()
            if not res:
                raise AuthenticationError()
            new_token = create_access_token(uid)
            return {"token": new_token, "user_id": uid}
        except AuthenticationError as ex_auth:
            return {'error': 'Authentication Failed!'}, 401
        except UserDoesNotExistError as ex_auth:
            return {'error': 'User Does Not Exist!'}, 500


class User(Resource):

    def __init__(self):
        self.count = 0

    @jwt_required()
    def get(self, uid=None):
        """
        Gets the information of a user by his/her ID
        :param uid:
        :return:
        """
        try:
            conn = sqlite3.connect('usersdb')
            cur = conn.cursor()
            current_user_id = get_jwt_identity()
            cur.execute('SELECT id, name FROM users WHERE id = ?', (current_user_id,))
            res = cur.fetchone()
            if not res:
                raise AuthenticationError()

            if uid is None:
                cur.execute('SELECT id, name FROM users')
                res = cur.fetchall()
                return [{'uid': item[0], 'name': item[1]} for item in res]
            else:
                cur.execute('SELECT id, name FROM users WHERE id = ?', (uid,))
                res = cur.fetchone()
                if not res:
                    return {}
                return {'uid': res[0], 'name': res[1]}, 200
        except (ConnectionError, RuntimeError) as e:
            return {'error': 'Operation Failed!'}, 500
        except AuthenticationError as ex:
            return {'error': 'Authentication Failed'}, 401
        else:
            return {'error': 'Operation Failed!'}, 500
        finally:
            conn.close()

    def post(self):
        try:
            conn = sqlite3.connect('usersdb')
            cur = conn.cursor()
            req_data = request.get_json()
            uid = self.count + 1
            cur.execute('INSERT INTO users VALUES(?, ?)', (uid, req_data['name']))
            self.count += 1
            conn.commit()
            return {'data': 'Success'}
        except (ConnectionError, RuntimeError) as e:
            return {'error': 'Operation Failed!'}
        else:
            return {'error': 'Operation Failed!'}
        finally:
            conn.close()

    def put(self, uid):
        try:
            conn = sqlite3.connect('usersdb')
            cur = conn.cursor()
            req_data = request.get_json()
            uid = self.count + 1
            cur.execute('UPDATE users set name = ? where id = ?', (req_data['name'], uid))
            conn.commit()
            return {'id': uid, 'name': req_data['name']}
        except (ConnectionError, RuntimeError) as e:
            return {'error': 'Operation Failed!'}
        else:
            return {'error': 'Operation Failed!'}
        finally:
            conn.close()

    def delete(self, uid):
        data = 'Hello ' + ('World!' if uid == '' else uid)
        return {'data': data}


class CreateTable(Resource):

    def post(self, tablename):
        try:
            conn = sqlite3.connect('usersdb')
            cur = conn.cursor()
            cur.execute('CREATE TABLE {}(id integer, name text)'.format(tablename))
            conn.commit()
            return {'data': 'Table Created'}
        except (ConnectionError, RuntimeError) as e:
            return {'error': 'Operation Failed!'}
        else:
            return {'error': 'Operation Failed!'}
        finally:
            conn.close()


api.add_resource(HelloWorld, '/hello', '/hello/<string:name>')
api.add_resource(Login, '/login', '/login/<int:uid>')
api.add_resource(User, '/user', '/user/<int:uid>')
api.add_resource(CreateTable, '/createtable/<string:tablename>')

if __name__ == '__main__':
    app.run(debug=True)
