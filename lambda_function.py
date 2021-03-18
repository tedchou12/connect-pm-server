from flask import Flask, render_template, make_response, redirect, request, session, url_for
from flask_cors import CORS
import os
import time
from datetime import date, datetime, timedelta
from src.pm_server.modules.config import config
from src.pm_server.modules.account import account
from src.pm_server.modules.credential import credential
from src.pm_server.modules.oidc import google, microsoft, hac
from src.pm_server.modules.app_session import app_session
from src.pm_server.modules.security import security
from src.pm_server.modules.crypt import crypt
from src.pm_server.modules.function import *
import json
import math
import base64
import codecs

obj_config = config()

app = Flask(__name__, static_folder=obj_config.params['static_path'], template_folder=obj_config.params['templates_path'])
app.secret_key = obj_config.params['flask_secret']

def lambda_cron() :
    return sync()

def header_template() :
    context_header = {'lang_home': lang('Home'),
                      'lang_title': '<span class="path" onclick="javascript: window.location=\'' + link('tenant') + '\'">' + lang('Home') + '</span>',
                      'lang_setting': lang('Setting'),
                      'link_home': link(''),
                      'link_setting': link('setting'),
                      'link_logout': link('logout'),
                      'lang_logout': lang('Logout')}

    return context_header

@app.route('/')
def index() :
    obj_account = account()
    obj_session = app_session()
    obj_credential = credential()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])
    else :
        return redirect(link('login'))

    credentials = obj_credential.list_credentials()
    list_credentials = []
    for credential_ele in credentials :
        list_credential = {}
        list_credential['url'] = credentials[credential_ele]['credential_url']
        list_credential['username'] = credentials[credential_ele]['credential_username']
        list_credentials.append(list_credential)

    context_header = header_template()
    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'val_accounts': list_credentials,
               'link_contact': link('contact'),
               'lang_url': lang('Service URL'),
               'lang_username': lang('Username'),
               'lang_password': lang('Password'),
               'lang_company_name': lang('Company Name'),
               'lang_contract_status': lang('Contract Status'),
               'lang_contract_valid': lang('Contract Valid'),
               'lang_edit': lang('Edit'),
               'lang_total': lang('Total'),
               }
    context_header.pop('lang_title')
    context = {**context, **context_header}

    return render_template('index.html', context=context)

@app.route('/api', methods=['GET', 'POST'])
def api() :
    obj_account = account()
    obj_session = app_session()
    obj_credential = credential()
    obj_crypt = crypt()

    if request.method == 'POST' :
        session_id = request.form['access_token']
    else :
        session_id = ''

    authorized = False
    list_credentials = []
    if obj_session.check_session(session_id) == True :
        obj_account.set_account(session['session_id'])
        authorized = True

        credentials = obj_credential.list_credentials()
        for credential_ele in credentials :
            list_credential = {}
            list_credential['url'] = base64.b64encode(credentials[credential_ele]['credential_url'].encode('utf-8')).decode('utf-8')
            list_credential['username'] = base64.b64encode(credentials[credential_ele]['credential_username'].encode('utf-8')).decode('utf-8')
            password = credentials[credential_ele]['credential_password']
            password = obj_crypt.encrypt(password)
            list_credential['password'] = password
            list_credentials.append(list_credential)

    return json.dumps({'authorized': authorized, 'data': list_credentials})

@app.route('/login', methods=['GET', 'POST'])
def login() :
    obj_account = account()
    obj_security = security()
    obj_session = app_session()
    oidc_google = google()
    oidc_microsoft = microsoft()
    oidc_hac = hac()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        return redirect(link(''))
    elif request.method == 'POST' :
        if request.form['hash'] == '' or obj_security.check_hash(request.form['hash']) != True :
            session['msg'] = lang('You did not pass the security check, please login again')
            username = request.form['email']
        elif request.form['email'] != '' and request.form['pass'] != '' and obj_account.check_account(request.form['email'], request.form['pass']) == True :
            session_hash = obj_session.save_session(session['account']['account_id'])
            if session_hash != False :
                context = {}
                response = make_response(redirect(link('')))
                response.set_cookie(key='session_id', value=session_hash)
                return response
        else :
            session['msg'] = lang('Incorrect Email or Password combination')
            username = request.form['email']
    else :
        username = ''

    if 'msg' in session and session['msg'] != '' :
        msg_status = True
        msg_content = session['msg']
        session['msg'] = ''
    else :
        msg_status = False
        msg_content = ''

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'msg_status': '' if msg_status == True else 'none',
               'msg_content': msg_content,
               'val_username': username,
               'val_hash': obj_security.get_hash(),
               'lang_username': lang('E-mail'),
               'lang_password': lang('Password'),
               'lang_login': lang('Log in'),
               'lang_forot_my_pass': lang('Forgot my Password?'),
               'lang_remember_me': lang('Remember this login'),
               'lang_or': lang('OR'),
               'link_google': oidc_google.auth_url(),
               'link_microsoft': oidc_microsoft.auth_url(),
               'link_hac': oidc_hac.auth_url(),
               'link_forgot': link('forgot')}

    return render_template('login.html', context=context)

@app.route('/callback', methods=['GET', 'POST'])
def callback() :
    obj_account = account()
    obj_session = app_session()
    oidc_google = google()
    oidc_microsoft = microsoft()
    oidc_hac = hac()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        return redirect(link(''))
    elif request.method == 'GET' :
        code = request.args.get('code')
        state = request.args.get('state')
        if state == 'microsoft' :
            if code != '' :
                data = oidc_microsoft.get_token(code)
                if 'email' in data and obj_account.check_account_email(data['email']) == True :
                    session_hash = obj_session.save_session(session['account']['account_id'])
                    if session_hash != False :
                        context = {}
                        response = make_response(redirect(link('')))
                        response.set_cookie(key='session_id', value=session_hash)
                        return response
                else :
                    session['msg'] = lang('Incorrect Account from Microsoft')
        elif state == 'google' :
            if code != '' :
                data = oidc_google.get_token(code)
                if 'email' in data and obj_account.check_account_email(data['email']) == True :
                    session_hash = obj_session.save_session(session['account']['account_id'])
                    if session_hash != False :
                        context = {}
                        response = make_response(redirect(link('')))
                        response.set_cookie(key='session_id', value=session_hash)
                        return response
                else :
                    session['msg'] = lang('Incorrect Account from Google')
        else :
            if code != '' :
                data = oidc_hac.get_token(code)
                if 'email' in data and obj_account.check_account_email(data['email']) == True :
                    session_hash = obj_session.save_session(session['account']['account_id'])
                    if session_hash != False :
                        context = {}
                        response = make_response(redirect(link('')))
                        response.set_cookie(key='session_id', value=session_hash)
                        return response
                else :
                    session['msg'] = lang('Incorrect Account from HAC')

        return redirect(link('login'))
    else :
        return redirect(link('login'))

@app.route('/logout')
def logout() :
    obj_account = account()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        obj_session.logout_session()

        return redirect(link('login'))
    else :
        return redirect(link('login'))

if __name__ == '__main__' :
    cors = CORS(app, resources={'*': {'origins': '*'}})
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
