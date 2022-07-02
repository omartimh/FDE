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

class Signature():
    def add_signature(self, db, params):
        sql = '''INSERT INTO sessions (signature_img, created, modified, deleted)
        VALUES (%s, %s, %s, %s)'''
        bindvars = [params[0], params[1], params[2], params[3]]
        db.execute(sql, bindvars, True)
    def predict_signature(self, model_name, file):
        img = tf.io.read_file('signatures/' + file)
        img = tf.image.decode_jpeg(img, channels = 3)
        img = tf.image.resize(img, [320, 240])
        img = tf.expand_dims(img, axis = 0)
        model = tf.keras.models.load_model('cnn/' + model_name)
        result = model.predict(img)[0]
        return result