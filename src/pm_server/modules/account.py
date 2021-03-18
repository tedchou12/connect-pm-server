from flask import session
from datetime import date, datetime, timedelta
import json
import os
import pickle
import requests
import time
from .db import db
import random
import string
import hashlib

class account :
    def __init__(self) :
        self.table = 'account'
        self.account = {}
        # reset code for password reset works for 48 hours
        self.reset_duration = 60 * 60 * 24 * 2

    def list_accounts(self, index='email') :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + '')
        data = ()

        accounts =  obj_database.select(query, data)
        results = {}
        for account1 in accounts :
            if index == 'sfdc' :
                results[account1['account_sfdc']] = account1
            else :
                results[account1['account_email']] = account1

        return results

    def add_account(self, sfdc='', name='', email='') :
        obj_database = db()
        query = ('INSERT INTO ' + self.table + ' (account_sfdc, account_name, account_email, account_pass, account_salt) VALUES (%s, %s, %s, %s, %s)')
        data = (sfdc, name, email, '', '')

        return obj_database.insert(query, data)

    def update_account(self, user_id='', account_lang='', account_info={}, password='') :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + ' WHERE account_id=%s')
        data = (user_id, )
        users = obj_database.select(query, data)

        if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
            account_data = {}
        else :
            account_data = json.loads(users[0]['account_data'])
        if account_lang == 'en' :
            account_data['lang'] = 'en'
        elif account_lang == 'ja' :
            account_data['lang'] = 'ja'
        elif account_lang == 'zh' :
            account_data['lang'] = 'zh'
        if bool(account_info) != False :
            for item in account_info :
                account_data[item] = account_info[item]
        if password != '' :
            salt = self.salt_generator()
            new_pass = self.pass_hash(password, salt)
            query = ('UPDATE ' + self.table + ' SET account_data=%s, account_pass=%s, account_salt=%s, account_reset=%s, account_reset_datetime=%s WHERE account_id=%s')
            data = (json.dumps(account_data), new_pass, salt, '', None, user_id)
        else :
            query = ('UPDATE ' + self.table + ' SET account_data=%s WHERE account_id=%s')
            data = (json.dumps(account_data), user_id)

        if obj_database.update(query, data) == True :
            return True
        else :
            return False

    # usual login
    def check_account(self, email, password) :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_email=%s')
        data = (email, )
        users = obj_database.select(query, data)

        if len(users) > 0 and self.pass_hash(password, users[0]['account_salt']) == users[0]['account_pass'] :
            if users[0]['account_reset'] != '' :
                query = ('UPDATE ' + self.table + ' SET account_reset=%s, account_reset_datetime=%s WHERE account_id=%s')
                data = ('', None, users[0]['account_id'])
                obj_database.update(query, data)
            session['account'] = users[0]
            if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
                session['account_data'] = {}
            else :
                session['account_data'] = json.loads(users[0]['account_data'])
            if 'lang' in session['account_data'] :
                session['lang'] = session['account_data']['lang']

            return True
        else :
            return False

    # login by oidc
    def check_account_email(self, email) :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_email=%s')
        data = (email, )
        users = obj_database.select(query, data)

        if len(users) > 0 and users[0]['account_email'] == email :
            if users[0]['account_reset'] != '' :
                query = ('UPDATE ' + self.table + ' SET account_reset=%s, account_reset_datetime=%s WHERE account_id=%s')
                data = ('', None, users[0]['account_id'])
                obj_database.update(query, data)
            session['account'] = users[0]
            if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
                session['account_data'] = {}
            else :
                session['account_data'] = json.loads(users[0]['account_data'])
            if 'lang' in session['account_data'] :
                session['lang'] = session['account_data']['lang']

            return True
        else :
            return False

    def set_account(self, user_id) :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_id=%s')
        data = (user_id, )
        users = obj_database.select(query, data)

        if len(users) > 0 :
            session['account'] = users[0]
            if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
                session['account_data'] = {}
            else :
                session['account_data'] = json.loads(users[0]['account_data'])
            if 'lang' in session['account_data'] :
                session['lang'] = session['account_data']['lang']
            return True
        else :
            return False

    def get_account(self, user_id) :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_id=%s')
        data = (user_id, )
        users = obj_database.select(query, data)

        if len(users) > 0 :
            data = users[0]
            if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
                data['account_data'] = {}
            else :
                data['account_data'] = json.loads(users[0]['account_data'])
            data['account_phone'] = data['account_data']['phone']
            return data
        else :
            return False

    def get_account_by_email(self, user_email='') :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_email=%s')
        data = (user_email, )
        users = obj_database.select(query, data)

        if len(users) > 0 :
            data = users[0]
            if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
                data['account_data'] = {}
            else :
                data['account_data'] = json.loads(users[0]['account_data'])
            data['account_phone'] = data['account_data']['phone']
            return data
        else :
            return False

    def get_account_by_sfdc(self, sfdc='') :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_sfdc=%s')
        data = (sfdc, )
        users = obj_database.select(query, data)

        if len(users) > 0 :
            data = users[0]
            if 'account_data' not in users[0] or users[0]['account_data'] == '' or users[0]['account_data'] == None :
                data['account_data'] = {}
            else :
                data['account_data'] = json.loads(users[0]['account_data'])
            data['account_phone'] = data['account_data']['phone']
            return data
        else :
            return False

    def password_reset(self, user_id) :
        obj_database = db()
        hash = self.hash_generator()
        query = ('UPDATE ' + self.table + ' SET account_reset=%s, account_reset_datetime=%s WHERE account_id=%s')
        data = (hash, time.strftime('%Y-%m-%d %H:%M:%S'), user_id)
        if obj_database.update(query, data) == True :
            return hash
        else :
            return False

    def update_password(self, user_id, code='', password='') :
        obj_database = db()
        query = ('SELECT * FROM ' + self.table + ' WHERE account_id=%s')
        data = (user_id, )
        users = obj_database.select(query, data)

        if len(users) > 0 :
            if users[0]['account_reset'] == code and (int(datetime.now().timestamp()) - int(datetime.timestamp(users[0]['account_reset_datetime']))) < self.reset_duration :
                salt = self.salt_generator()
                new_pass = self.pass_hash(password, salt)
                query = ('UPDATE ' + self.table + ' SET account_pass=%s, account_salt=%s, account_reset=%s, account_reset_datetime=%s WHERE account_id=%s')
                data = (new_pass, salt, '', None, user_id)
                if obj_database.update(query, data) == True :
                    return True

        return False

    def delete_account(self, email='') :
        obj_database = db()
        query = ('DELETE FROM ' + self.table + ' WHERE account_email=%s')
        data = (email, )

        return obj_database.delete(query, data)

    def pass_hash(self, password, salt) :
        if salt == '' :
            salt = self.salt_generator()

        string = str(password) + str(salt)

        return hashlib.md5(string.encode("utf-8")).hexdigest()

    def salt_generator(self) :
        letters = string.ascii_lowercase + '1234567890'
        return ''.join(random.choice(letters) for i in range(8))

    def hash_generator(self) :
        letters = string.ascii_lowercase + '1234567890'
        return ''.join(random.choice(letters) for i in range(32))
