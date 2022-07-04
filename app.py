import os
import uuid
import hashlib
from flask import Flask, redirect, render_template, url_for, request, session
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_fontawesome import FontAwesome
from werkzeug.utils import secure_filename
from models import Postgres, User, Document

from dotenv import load_dotenv
load_dotenv()

db = Postgres()
db.connect(os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOSTNAME'), os.getenv('DB_DATABASE'))

app = Flask(__name__)
app.secret_key = 'X'

nav = Nav(app)
nav.register_element('main_nav',Navbar('nav',
    View('Dashboard', 'dashboard'),
    View('Documents', 'documents'),
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
                hashed_password = password + app.secret_key
                hashed_password = hashlib.md5(hashed_password.encode()).hexdigest()
                if hashed_password != user_password:
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
            hashed_password = password + app.secret_key
            hashed_password = hashlib.md5(hashed_password.encode()).hexdigest()
            params = [utype, nid, username, email, hashed_password, name, phone, gender, dob, created, modified, deleted]
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
                    users = User().get_users_by_nid(db, nid)
                return render_template('users.html', title = 'Manage Users', users = users)

@app.route('/documents', methods = ['GET', 'POST'])
def documents():
    if request.method == 'GET':
        if not request.args.get('param') or request.args.get('param') == 'manage_documents':
            documents = Document().get_all_documents(db)
            params = []
            for document in documents:
                document_id = document[0]
                details = Document().get_document_details(db, document_id)
                title = document[1]
                status_id = details[4]
                date = str(document[5]).split(' ')[0]
                status = Document().get_status_by_id(db, status_id)
                param = [document_id, title, status, date]
                params.append(param)
            return render_template('documents.html', title = 'Manage Documents', params = params)
        elif request.args.get('param') == 'add_document':
            return render_template('documents.html', title = 'Add Document')
        elif request.args.get('param') == 'view_document':
            document_id = request.args.get('document_id')
            document = Document().get_document_by_id(db, document_id)
            document_title = document[1]
            document_description = document[2]
            signature_txt = document[3]
            signature_img = document[4]
            created = str(document[5]).split(' ')[0]
            modified = str(document[6]).split(' ')[0]
            details = Document().get_document_details(db, document_id)
            details_id = details[0]
            examiner_id = details[2]
            owner_id = details[3]
            user = User().get_user_by_id(db, owner_id)
            nid = user[2]
            status_id = details[4]
            status = Document().get_status_by_id(db, status_id)
            model_id = details[5]
            model = Document().get_model_by_id(db, model_id)
            class_id = details[6]
            prediction = Document().get_class_by_id(db, class_id)
            score1 = details[7]
            score2 = details[8]
            params = [document_id, created, modified, document_title, document_description, nid, owner_id,
            signature_img, signature_txt, model, prediction, score1, score2, status, details_id]
            return render_template('documents.html', title = 'View Document', params = params)
        elif request.args.get('param') == 'edit_documents':
            return render_template('documents.html', title = 'Edit Document')
        elif request.args.get('param') == 'edit_status':
            document_id = request.args.get('document_id')
            details_id = request.args.get('details_id')
            status = request.args.get('status')
            status_id = Document().get_status_by_name(db, status)
            modified = 'Now'
            params = [document_id, details_id, status_id, modified]
            Document().update_status(db, params)
            return redirect(url_for('documents', param = 'view_document', document_id = document_id))
    if request.method == 'POST':
        if request.args.get('param') == 'add_document':
            empty = False
            title = request.form.get('title')
            description = request.form.get('description')
            signature_txt = request.form.get('signature_txt')
            nid = request.form.get('nid')
            model_id = request.form.get('model')
            file = request.files['signature_img']
            inputs = [title, description, nid, model_id, file, signature_txt]
            for input in inputs:
                if input == '' or input == None:
                    empty = True
                    break
            if empty:
                return render_template('documents.html', title = 'Add Document', params = inputs, error = 'Please, Fill in all empty fields!')
            else:
                user = User().get_user_by_nid(db, nid)
                if not user:
                    return render_template('documents.html', title = 'Add Document', params = inputs, error = 'Please, Use a valid National ID!')
                else:
                    file_ext = file.filename.split('.').pop()
                    unique_filename = str(uuid.uuid4())
                    file.filename = unique_filename + '.' + file_ext
                    signature_img = file.filename
                    created = 'Now'
                    modified = 'Now'
                    deleted = False
                    params = [title, description, signature_txt, signature_img, created, modified, deleted]
                    document_id = Document().add_document(db, params)
                    examiner_id = session['user'][0]
                    owner_id = user[0]
                    status_id = 1
                    model = Document().get_model_by_id(db, model_id)
                    model = str(model) + '.h5'
                    file.save('static/signatures/' + secure_filename(signature_img))
                    prediction = Document().predict_signature(model, signature_img)
                    fscore = prediction[0]
                    gscore = prediction[1]
                    score1 = str(fscore)
                    score2 = str(gscore)
                    if fscore > gscore:
                        pclass = 'Forged'
                    elif fscore < gscore:
                        pclass = 'Genuine'
                    class_id = Document().get_class_by_name(db, pclass)
                    params = [document_id, examiner_id, owner_id, status_id, model_id, class_id, score1, score2]
                    Document().add_document_details(db, params)
                    return redirect(url_for('documents', param = 'view_document', document_id = document_id))
        if request.args.get('param') == 'edit_document':
            pass

##############################################################################################################################

if __name__ == "__main__":
    app.run(debug=True)