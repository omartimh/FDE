import uuid
# from datetime import datetime
from flask import Flask, render_template, request
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_fontawesome import FontAwesome
from werkzeug.utils import secure_filename
from models import Postgres, User, Signature

POSTGRES_USERNAME = 'postgres'
POSTGRES_PASSWORD = 'psql'
POSTGRES_HOSTNAME = 'localhost'
POSTGRES_DATABASE = 'fde'

db = Postgres()
db.connect(POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_HOSTNAME, POSTGRES_DATABASE)

app = Flask(__name__)
fa = FontAwesome(app)
nav = Nav(app)
nav.register_element('main_nav',Navbar('nav',
    View('Home', 'home'),
    View('Documents', 'documents'),
    View('Users', 'users')
))

##############################################################################################################################

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/users',  methods = ['GET', 'POST'])
def users():
    if request.method == 'GET':
        if request.args.get('param') == 'manage_users' or not request.args.get('param'):
            users = User().get_all_users(db)
            return render_template('users.html', title = 'Manage Users', users = users)
        elif request.args.get('param') == 'add_user':
            return render_template('users.html', title = 'Add User')
        elif request.args.get('param') == 'view_user':
            id = request.args.get('id')
            user = User().get_user_by_id(db, id)
            return render_template('users.html', title = 'View User', user = user)
        elif request.args.get('param') == 'edit_user':
            id = request.args.get('id')
            user = User().get_user_by_id(db, id)
            return render_template('users.html', title = 'Edit User', user = user)
        elif request.args.get('param') == 'delete_user':
            id = request.args.get('id')
            user = User().delete_user(db, id)
            users = User().get_all_users(db)
            return render_template('users.html', title = 'Manage Users', users = users)
    elif request.method == 'POST':
        if request.args.get('param') == 'add_user':
            empty = False
            unmatch = False
            utype = request.form.get('utype')
            nid = request.form.get('nid')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            name = request.form.get('name')
            params = [utype, nid, username, email, password, name]
            for param in params:
                if param == '' or param == None:
                    empty = True
                    break
            if password != confirm_password:
                unmatch = True
            exists = User().get_user_by_username(db, username)
            if empty:
                return render_template('users.html', title = 'Add User', params = params, error = 'Please, fill in all empty fields!')
            elif unmatch:
                return render_template('users.html', title = 'Add User', params = params, error = 'Passwords do not match!')
            elif exists:
                return render_template('users.html', title = 'Add User', params = params, error = 'Username already exists!')
            else:
                User().add_user(db, params)
                users = User().get_all_users(db)
                return render_template('users.html', title = 'Manage Users', users = users)
        elif request.args.get('param') == 'update_user':
            pass

@app.route('/documents', methods = ['GET', 'POST'])
def documents():
    if request.method == 'GET':
        return render_template('documents.html', title = 'Classification Setup')
    if request.method == 'POST':
        model_name = request.form['model'] + '.h5'
        file = request.files['file']
        file_ext = file.filename.split('.').pop()
        unique_filename = str(uuid.uuid4())
        file.filename = unique_filename + '.' + file_ext
        file.save('signatures/' + secure_filename(file.filename))
        params = ['NOW', 'NOW', False, file.filename]
        signature = Signature()
        signature.add_signature(db, params)
        result = signature.predict_signature(model_name, file.filename)
        return render_template('documents.html', title = 'Classification Result', result = result)

##############################################################################################################################

if __name__ == "__main__":
    app.run(debug=True)