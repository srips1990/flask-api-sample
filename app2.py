from flask import Flask, make_response
from flask_restful import Api, Resource, request
import sqlite3
from exptns import AuthenticationError, UserDoesNotExistError

# Press the green button in the gutter to run the script.
app = Flask(__name__)

api = Api(app)


class HelloWorld(Resource):

    def get(self, name):
        return {'msg': f"Hi {name}"}


class Home(Resource):

    def get(self):
        return {'msg': "Hey you"}, 200

if __name__ == '__main__':
    api.add_resource(Home, '/')
    api.add_resource(HelloWorld, '/hello/<string:name>')
    # api.add_resource(Login, '/login', '/login/<int:uid>')
    # api.add_resource(User, '/user', '/user/<int:uid>')
    # api.add_resource(CreateTable, '/createtable/<string:tablename>')
    app.run(debug=True)
