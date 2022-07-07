import psycopg2
from psycopg2 import pool
import tensorflow as tf

class Postgres():
    def connect(self, USERNAME, PASSWORD, HOSTNAME, DATABASE):
        try:
            self.pool = pool.SimpleConnectionPool(1, 1,
                user = USERNAME,
                password = PASSWORD,
                host = HOSTNAME,
                database = DATABASE
            )
        except (Exception, psycopg2.DatabaseError) as error:
            print('>>> ERROR: Postgres Database Connection', error)
            raise
        else:
            self.db = self.pool.getconn()
            self.cursor = self.db.cursor()
    def disconnect(self):
        try:
            if self.pool:
                self.pool.putconn(self.db)
                self.pool.closeall
        except:
            pass
    def execute(self, sql, bindvars = None, commit = False):
        try:
            self.cursor.execute(sql, bindvars)
        except (Exception, psycopg2.DatabaseError) as error:
            print('>>> ERROR: Postgres SQL Execution', error)
            raise
        else:
            if commit:
                self.db.commit()

class User():
    def add_user(self, db, params):
        sql = '''INSERT INTO users (utype_id, nid, username, email, password, name, phone, gender, dob, created, modified, deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        bindvars = [params[0], params[1], params[2], params[3], params[4], params[5],
        params[6], params[7], params[8], params[9], params[10], params[11]]
        result = db.execute(sql, bindvars, True)
        return result
    def get_user_by_id(self, db, id):
        user = None
        sql = '''SELECT * FROM users WHERE id = %s AND deleted = %s'''
        bindvars = [id, False]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            user = result[0]
        return user
    def get_user_by_nid(self, db, nid):
        user = None
        sql = '''SELECT * FROM users WHERE nid = %s AND deleted = %s'''
        bindvars = [nid, False]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            user = result[0]
        return user
    def get_users_by_nid(self, db, nid):
        sql = '''SELECT * FROM users WHERE nid = %s AND deleted = %s'''
        bindvars = [nid, False]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        return result
    def get_user_by_username(self, db, username):
        user = None
        sql = '''SELECT * FROM users WHERE username = %s AND deleted = %s'''
        bindvars = [username, False]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            user = result[0]
        return user
    def get_all_users(self, db):
        sql = '''SELECT * FROM users WHERE deleted = False ORDER BY modified DESC'''
        db.execute(sql)
        result = db.cursor.fetchall()
        return result
    def update_user(self, db, params):
        sql = '''UPDATE users SET utype_id = %s, nid = %s, username = %s, email = %s, password = %s, name = %s,
        phone = %s, gender = %s, dob = %s, modified = %s WHERE id = %s'''
        bindvars = [params[1], params[2], params[3], params[4], params[5], params[6], params[7], params[8], params[9], params[10], params[0]]
        result = db.execute(sql, bindvars, True)
        return result
    def delete_user(self, db, id):
        sql = '''UPDATE users SET deleted = %s WHERE id = %s'''
        bindvars = [True, id]
        result = db.execute(sql, bindvars, True)
        return result

class Document():
    def predict_signature(self, model_name, file):
        img = tf.io.read_file('static/signatures/' + file)
        img = tf.image.decode_jpeg(img, channels = 3)
        img = tf.image.resize(img, [320, 240])
        img = tf.expand_dims(img, axis = 0)
        model = tf.keras.models.load_model('cnn/' + model_name)
        prediction = model.predict(img)[0]
        return prediction
    def get_dashboard_items(self, db):
        total_predictions = None
        verified_signatures = None
        genuine_signatures = None
        forged_signatures = None
        sql = '''SELECT COUNT(*) FROM document_details'''
        db.execute(sql)
        result = db.cursor.fetchall()[0]
        if result:
            total_predictions = result[0]
        sql = '''SELECT COUNT(*) FROM document_details WHERE status_id = %s'''
        bindvars = [3]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()[0]
        if result:
            verified_signatures = result[0]
        sql = '''SELECT COUNT(*) FROM document_details WHERE class_id = %s'''
        bindvars = [2]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()[0]
        if result:
            genuine_signatures = result[0]
        sql = '''SELECT COUNT(*) FROM document_details WHERE class_id != %s'''
        bindvars = [2]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()[0]
        if result:
            forged_signatures = result[0]
        items = [total_predictions, verified_signatures, genuine_signatures, forged_signatures]
        return items
    def get_all_documents(self, db):
        sql = '''SELECT * FROM documents WHERE deleted = %s'''
        bindvars = [False]
        db.execute(sql, bindvars)
        documents = db.cursor.fetchall()
        return documents
    def get_document_details(self, db, document_id, examiner_id):
        details = None
        sql = '''SELECT * FROM document_details WHERE document_id = %s and examiner_id = %s'''
        bindvars = [document_id, examiner_id]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            details = result[0]
        return details
    def get_document_by_id(self, db, document_id):
        sql = '''SELECT * FROM documents WHERE id = %s'''
        bindvars = [document_id]
        db.execute(sql, bindvars)
        document = db.cursor.fetchall()[0]
        return document
    def get_title(self, db, document_id):
        title = None
        sql = '''SELECT * FROM documents WHERE id = %s'''
        bindvars = [document_id]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            title = result[0][1]
        return title
    def get_status_by_id(self, db, status_id):
        status = None
        sql = '''SELECT * FROM status WHERE id = %s'''
        bindvars = [status_id]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()[0]
        if result:
            status = result[1]
        return status
    def get_status_by_name(self, db, status):
        status_id = None
        sql = '''SELECT * FROM status WHERE status = %s'''
        bindvars = [status]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()[0]
        if result:
            status_id = result[0]
        return status_id
    def get_model_by_id(self, db, model_id):
        model = None
        sql = '''SELECT * FROM models WHERE id = %s'''
        bindvars = [model_id]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()[0]
        if result:
            model = result[1]
        return model
    def get_class_by_id(self, db, class_id):
        prediction = None
        sql = '''SELECT * FROM classes WHERE id = %s'''
        bindvars = [class_id]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            prediction = result[0][1]
        return prediction
    def get_class_by_name(self, db, pclass):
        class_id = None
        sql = '''SELECT * FROM classes WHERE class = %s'''
        bindvars = [pclass]
        db.execute(sql, bindvars)
        result = db.cursor.fetchall()
        if result:
            class_id = result[0][0]
        return class_id
    def add_document(self, db, params):
        sql = '''INSERT INTO documents (title, description, signature_txt, signature_img, created, modified, deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id'''
        bindvars = [params[0], params[1], params[2], params[3], params[4], params[5], params[6]]
        db.execute(sql, bindvars, True)
        document_id = db.cursor.fetchone()[0]
        return document_id
    def add_document_details(self, db, params):
        sql = '''INSERT INTO document_details (document_id, examiner_id, owner_id, status_id, model_id, class_id, score1, score2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        bindvars = [params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7]]
        db.execute(sql, bindvars, True)
    def update_document(self, db, params):
        pass
    def update_status(self, db, params):
        sql = '''UPDATE document_details SET status_id = %s WHERE id = %s'''
        bindvars = [params[2], params[1]]
        db.execute(sql, bindvars, True)
        sql = '''UPDATE documents SET modified = %s WHERE id = %s'''
        bindvars = [params[3], params[0]]
        db.execute(sql, bindvars, True)
    def delete_document(self, db, id):
        pass