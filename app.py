import os
import uuid
from flask import Flask, redirect, render_template, url_for, request, session
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_fontawesome import FontAwesome
from werkzeug.utils import secure_filename
from models import Postgres, User, Signature

from dotenv import load_dotenv
load_dotenv()

db = Postgres()
db.connect(os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOSTNAME'), os.getenv('DB_DATABASE'))

app = Flask(__name__)
app.secret_key = 'X'

nav = Nav(app)
nav.register_element('main_nav',Navbar('nav',
    View('Dashboard', 'dashboard'),
    View('Documents', 'dashboard'),
    View('Users', 'users'),
    View('Settings', 'dashboard'),
    View('Profile', 'dashboard'),
    View('Logout', 'logout')
))

fa = FontAwesome(app)

##############################################################################################################################

@app.route('/')
def dashboard():
    if not 'user' in session:
        return redirect(url_for('login'))
    else:
        return render_template('dashboard.html')

@app.route('/login',  methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if not 'user' in session:
            return render_template('login.html')
        else:
            return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html',  error = 'Please, Fill in all empty fields!')
        else:
            user = User().get_user_by_username(db, username)
            if not user:
                return render_template('login.html',  error = 'Incorrect USERNAME or PASSWORD!')
            else:
                user_password = user[5]
                if password != user_password:
                    return render_template('login.html',  error = 'Incorrect USERNAME or PASSWORD!')
                else:
                    session['user'] = user
                    return redirect(url_for('dashboard'))

@app.route('/logout',  methods = ['GET', 'POST'])
def logout():
    if request.method == 'GET':
        session.pop('user', None)
        return redirect(url_for('login'))

@app.route('/users',  methods = ['GET', 'POST'])
def users():
    if request.method == 'GET':
        if not request.args.get('param') or request.args.get('param') == 'manage_users':
            users = User().get_all_users(db)
            return render_template('users.html', title = 'Manage Users', users = users)
        elif request.args.get('param') == 'add_user':
            return render_template('users.html', title = 'Add User')
        elif request.args.get('param') == 'view_user':
            id = request.args.get('id')
            user = User().get_user_by_id(db, id)
            return render_template('users.html', title = 'View User', params = user)
        elif request.args.get('param') == 'edit_user':
            id = request.args.get('id')
            user = User().get_user_by_id(db, id)
            return render_template('users.html', title = 'Edit User', params = user)
        elif request.args.get('param') == 'delete_user':
            id = request.args.get('id')
            user = User().delete_user(db, id)
            users = User().get_all_users(db)
            return render_template('users.html', title = 'Manage Users', users = users)
    elif request.method == 'POST':
        if request.args.get('param') == 'add_user':
            empty = False
            unmatch = False
            username = request.form.get('username')
            utype = request.form.get('utype')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            name = request.form.get('name')
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            dob = request.form.get('dob')
            nid = request.form.get('nid')
            created = 'Now'
            modified = 'Now'
            deleted = False
            params = [utype, nid, username, email, password, name, phone, gender, dob, created, modified, deleted]
            for param in params:
                if param == '' or param == None:
                    empty = True
                    break
            if password != confirm_password:
                unmatch = True
            exists = User().get_user_by_username(db, username)
            if empty:
                return render_template('users.html', title = 'Add User', params = params, error = 'Please, Fill in all empty fields!')
            elif unmatch:
                return render_template('users.html', title = 'Add User', params = params, error = 'Passwords do not match!')
            elif exists:
                return render_template('users.html', title = 'Add User', params = params, error = 'Username already exists!')
            else:
                User().add_user(db, params)
                users = User().get_all_users(db)
                return render_template('users.html', title = 'Manage Users', users = users)
        elif request.args.get('param') == 'edit_user':
            empty = False
            unmatch = False
            id = request.form.get('id')
            username = request.form.get('username')
            last_username = request.form.get('last_username')
            utype = request.form.get('utype')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            name = request.form.get('name')
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            dob = request.form.get('dob')
            nid = request.form.get('nid')
            modified = 'NOW'
            params = [id, utype, nid, username, email, password, name, phone, gender, dob, modified]
            for param in params:
                if param == '' or param == None:
                    empty = True
                    break
            if password != confirm_password:
                unmatch = True
            exists = User().get_user_by_username(db, username)
            if empty:
                return render_template('users.html', title = 'Edit User', params = params, error = 'Please, Fill in all empty fields!')
            elif unmatch:
                return render_template('users.html', title = 'Edit User', params = params, error = 'Passwords do not match!')
            elif exists and username != last_username:
                return render_template('users.html', title = 'Edit User', params = params, error = 'Username already exists!')
            else:
                User().update_user(db, params)
                user = User().get_user_by_id(db, id)
                return render_template('users.html', title = 'View User', params = user)
        elif request.args.get('param') == 'search_user':
                nid = request.form.get('nid')
                if not nid:
                    users = User().get_all_users(db)
                else:
                    users = User().get_user_by_nid(db, nid)
                return render_template('users.html', title = 'Manage Users', users = users)

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