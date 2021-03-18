from flask import make_response, request, session
from datetime import date, datetime, timedelta
from .db import db
import time
import random
import string

class app_session :
    def __init__(self):
        self.table = 'session'
        self.session_account = 0
        self.session_duration = 60 * 60 * 24 * 7

    def save_session(self, user) :
        obj_database = db()
        query = ('INSERT INTO ' + self.table + ' (session_hash, session_user, session_time) VALUES (%s, %s, %s)')
        session_hash = self.hash_generator()
        data = (session_hash, user, time.strftime('%Y-%m-%d %H:%M:%S'))

        if obj_database.insert(query, data) != False :
            return session_hash
        else :
            return False

    def check_session(self, session_id='') :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE session_hash=%s AND session_logout!=%s')
        if session_id == '' :
            session_hash = request.cookies.get('session_id', None)
        else :
            session_hash = session_id
        data = (session_hash, 1, )
        sessions = obj_database.select(query, data)

        if len(sessions) > 0 :
            if int(datetime.now().timestamp()) - int(datetime.timestamp(sessions[0]['session_time'])) < self.session_duration :
                session['session_id'] = sessions[0]['session_user']
                return True
            else :
                return False
        else :
            return False

    def logout_session(self) :
        obj_database = db()
        session_hash = request.cookies.get('session_id', None)
        query = ('UPDATE ' + self.table + ' SET session_logout=%s WHERE session_hash=%s')
        data = (1, session_hash)
        session['session_id'] = ''
        session['tenant'] = ''
        for item in session :
            session[item] = ''
        if obj_database.update(query, data) == True :
            return True
        else :
            return False

    def set_message(self, text='') :
        session['message'] = text

    def get_message(self) :
        if session['message'] != '' :
             message = session['message']
             session['message'] = ''
             return message

        return ''

    def hash_generator(self) :
        letters = string.ascii_lowercase + '1234567890'
        return ''.join(random.choice(letters) for i in range(32))
