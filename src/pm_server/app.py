from flask import Flask, render_template, make_response, redirect, request, session
import os
import time
from datetime import date, datetime, timedelta
from modules.config import config
from modules.account import account
from modules.tenant import tenant
from modules.contact import contact
from modules.oidc import google, microsoft
from modules.app_session import app_session
from modules.sfdc import sfdc
from modules.one_garden import one_garden
from modules.function import *

obj_config = config()

app = Flask(__name__, static_folder=obj_config.params['resources_path'])
app.secret_key = obj_config.params['flask_secret']

def header_template() :
    context_header = {'lang_home': lang('Home'),
                      'lang_setting': lang('Setting'),
                      'link_home': link('/'),
                      'link_setting': link('/setting'),
                      'link_logout': link('/logout'),
                      'lang_logout': lang('Logout')}

    return context_header

@app.route('/')
def index() :
    obj_account = account()
    obj_tenant = tenant()
    obj_contact = contact()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])
    else :
        return redirect(link('/login'))

    # selecting which tenant to view
    if 'tenant' not in session or session['tenant'] is None or session['tenant'] == '' :
        return redirect(link('/tenant'))

    contacts = obj_contact.get_contacts_by_tenant(session['tenant'])
    list_accounts = []
    for contact1 in contacts :
        account_ele = obj_account.get_account(contact1['contact_account'])
        account_ele['contact'] = contact1['contact_contact']
        account_ele['renew'] = contact1['contact_renew']
        account_ele['emergency'] = contact1['contact_emergency']
        list_accounts.append(account_ele)
    tenant_data = obj_tenant.get_tenant(session['tenant'])
    list_domains = [{'label': lang('Main'), 'value': tenant_data['tenant_domain']}]
    for domain in tenant_data['tenant_domains'] :
        domain_ele = {'label': '', 'value': domain}
        list_domains.append(domain_ele)
    services = {'hac': 0, 'hsb': 0, 'hdc': 0, 'dlp': 0, 'arc': 0, 'hos': 0}
    for service in services :
        if service in tenant_data['tenant_licenses'] :
            services[service] = int(tenant_data['tenant_licenses'][service])
    if 'end_date' in tenant_data['tenant_licenses'] :
        end_date = tenant_data['tenant_licenses']['end_date']
    else :
        end_date = ''
    if 'price' in tenant_data['tenant_licenses'] :
        total = tenant_data['tenant_licenses']['price']
    else :
        total = ''

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'link_contact': link('/contact'),
               'lang_name': lang('Name'),
               'lang_email': lang('Email'),
               'lang_phone': lang('Phone'),
               'lang_normal': lang('Normal'),
               'lang_renewal': lang('Renewal'),
               'lang_emergency': lang('Emergency'),
               'lang_domain': lang('Domain'),
               'lang_service': lang('Service'),
               'lang_licenses': lang('Licenses'),
               'lang_hac': lang('HAC'),
               'lang_hsb': lang('HSB'),
               'lang_hdc': lang('HDC'),
               'lang_dlp': lang('DLP'),
               'lang_arc': lang('ARC'),
               'lang_hos': lang('HOS'),
               'lang_company_name': lang('Company Name'),
               'lang_contract_status': lang('Contract Status'),
               'lang_contract_valid': lang('Contract Valid'),
               'lang_edit': lang('Edit'),
               'lang_total': lang('Total'),
               'val_hac': services['hac'],
               'val_hsb': services['hsb'],
               'val_hdc': services['hdc'],
               'val_dlp': services['dlp'],
               'val_arc': services['arc'],
               'val_hos': services['hos'],
               'val_accounts': list_accounts,
               'val_domains': list_domains,
               'val_name': tenant_data['tenant_name'],
               'val_status': tenant_data['tenant_status'],
               'val_enddate': display_datetime(end_date),
               'show_total': obj_contact.check_contact_view_price(),
               'val_total': display_number(total)
               }
    context_header = header_template()
    context = {**context, **context_header}

    return render_template('index.html', context=context)

@app.route('/tenant', methods=['GET', 'POST'])
def select_tenant() :
    obj_account = account()
    obj_contact = contact()
    obj_tenant = tenant()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])
    else :
        return redirect(link('/login'))

    if request.method == 'POST' :
        if request.form['tenant'] != '' :
            list_tenants = obj_contact.get_contacts_by_account()
            if len(list_tenants) > 0 :
                for tenant1 in list_tenants :
                    if tenant1['contact_tenant'] == request.form['tenant'] :
                        session['contact'] = tenant1
                        session['tenant'] = tenant1['contact_tenant']
                        return redirect(link('/'))

    # selecting which tenant to view
    list_tenants = obj_contact.get_contacts_by_account()
    if len(list_tenants) == 1 :
        session['contact'] = list_tenants[0]
        session['tenant'] = list_tenants[0]['contact_tenant']
        return redirect(link('/'))

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'lang_tenant': lang('Select Tenant'),
               'lang_select': lang('Select'),
               'lang_save': lang('Save'),
               'val_tenants': list_tenants,
               'val_lang': session['lang']}
    context_header = header_template()
    context = {**context, **context_header}

    return render_template('tenant.html', context=context)

@app.route('/contact', methods=['GET', 'POST'])
def edit_contact() :
    obj_account = account()
    obj_contact = contact()
    obj_tenant = tenant()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])
    else :
        return redirect(link('/login'))

    # selecting which tenant to view
    if 'tenant' not in session or session['tenant'] is None or session['tenant'] == '' :
        return redirect(link('/tenant'))

    if request.method == 'POST' :

        obj_account.update_account(session['account']['account_id'], request.form['lang'])

        return redirect(link('/contact'))

    contacts = obj_contact.get_contacts_by_tenant(session['tenant'])
    list_accounts = []
    for contact1 in contacts :
        account_ele = obj_account.get_account(contact1['contact_account'])
        account_ele['contact'] = contact1['contact_contact']
        account_ele['renew'] = contact1['contact_renew']
        account_ele['emergency'] = contact1['contact_emergency']
        list_accounts.append(account_ele)

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'link_home': link('/'),
               'lang_name': lang('Name'),
               'lang_email': lang('Email'),
               'lang_phone': lang('Phone'),
               'lang_normal': lang('Normal'),
               'lang_renewal': lang('Renewal'),
               'lang_emergency': lang('Emergency'),
               'lang_cancel': lang('Cancel'),
               'lang_save': lang('Save'),
               'val_accounts': list_accounts}
    context_header = header_template()
    context = {**context, **context_header}

    return render_template('contact.html', context=context)

@app.route('/setting', methods=['GET', 'POST'])
def setting() :
    obj_account = account()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])
    else :
        return redirect(link('/login'))

    if request.method == 'POST' :
        obj_account.update_account(session['account']['account_id'], request.form['lang'])

        return redirect(link('/setting'))

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'lang_lang': lang('Language'),
               'lang_select': lang('Select'),
               'lang_ja': lang('Japanese'),
               'lang_en': lang('English'),
               'lang_save': lang('Save'),
               'val_lang': session['lang']}
    context_header = header_template()
    context = {**context, **context_header}

    return render_template('setting.html', context=context)

@app.route('/login', methods=['GET', 'POST'])
def login() :
    obj_account = account()
    obj_session = app_session()
    oidc_google = google()
    oidc_microsoft = microsoft()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        return redirect(link('/'))
    elif request.method == 'POST' :
        if request.form['email'] != '' and request.form['pass'] != '' and obj_account.check_account(request.form['email'], request.form['pass']) == True :
            session_hash = obj_session.save_session(session['account']['account_id'])
            if session_hash != False :
                context = {}
                response = make_response(redirect(link('/')))
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
               'lang_username': lang('E-mail'),
               'lang_password': lang('Password'),
               'lang_login': lang('Log in'),
               'lang_forot_my_pass': lang('Forgot my Password?'),
               'lang_remember_me': lang('Remember this login'),
               'link_google': oidc_google.auth_url(),
               'link_microsoft': oidc_microsoft.auth_url(),
               'link_forgot': link('/forgot')}

    return render_template('login.html', context=context)

@app.route('/callback', methods=['GET', 'POST'])
def callback() :
    obj_account = account()
    obj_session = app_session()
    oidc_google = google()
    oidc_microsoft = microsoft()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        return redirect(link('/'))
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
                        response = make_response(redirect(link('/')))
                        response.set_cookie(key='session_id', value=session_hash)
                        return response
                else :
                    session['msg'] = lang('Incorrect Account from Microsoft')
        else :
            if code != '' :
                data = oidc_google.get_token(code)
                if 'email' in data and obj_account.check_account_email(data['email']) == True :
                    session_hash = obj_session.save_session(session['account']['account_id'])
                    if session_hash != False :
                        context = {}
                        response = make_response(redirect(link('/')))
                        response.set_cookie(key='session_id', value=session_hash)
                        return response
                else :
                    session['msg'] = lang('Incorrect Account from Google')

        return redirect(link('/login'))
    else :
        return redirect(link('/login'))

@app.route('/logout')
def logout() :
    obj_account = account()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        obj_session.logout_session()

        return redirect(link('/login'))
    else :
        return redirect(link('/login'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot() :
    obj_account = account()
    obj_session = app_session()

    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        return redirect(link('/'))
    elif request.method == 'POST' :
        account_info = obj_account.get_account_by_email(request.form['email'])
        if account_info != False :
            hash = obj_account.password_reset(account_info['account_id'])
            if hash != False :
                mailbody = 'Your Reset code is: ' + hash + '\r\nPlease visit here to reset your password: ' + obj_config.params['hostname'] + 'reset?email=' + account_info['account_email'] + '&code=' + hash
                sendmail(account_info['account_email'], 'reset_password', mailbody)
    else :
        a = ''

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'lang_email': lang('E-mail'),
               'lang_reset_pass': lang('Reset Password'),
               'lang_login': lang('Return to Login'),
               'link_login': link('/login'),
               'link_forgot': link('/forgot')}

    return render_template('forgot.html', context=context)

@app.route('/reset', methods=['GET', 'POST'])
def reset() :
    obj_account = account()
    obj_session = app_session()

    val_email = ''
    val_code = ''
    if obj_session.check_session() == True :
        obj_account.set_account(session['session_id'])

        return redirect(link('/'))
    elif request.method == 'POST' :
        account_info = obj_account.get_account_by_email(request.form['email'])
        if account_info != False :
            if request.form['pass'] == request.form['con_pass'] :
                obj_account.update_password(account_info['account_id'], request.form['code'], request.form['pass'])

                return redirect(link('/login'))
    else :
        if request.args.get('email') != None :
            val_email = request.args.get('email')
        if request.args.get('code') != None :
            val_code = request.args.get('code')

    context = {'resources_path': obj_config.params['resources_path'],
               'title': obj_config.params['app_name'],
               'lang_password': lang('Password'),
               'lang_con_password': lang('Confirm Password'),
               'lang_code': lang('Code'),
               'lang_email': lang('E-mail'),
               'lang_reset_pass': lang('Reset Password'),
               'lang_login': lang('Return to Login'),
               'val_email': val_email,
               'val_code': val_code,
               'link_login': link('/login'),
               'link_forgot': link('/forgot')}

    return render_template('reset.html', context=context)

@app.route('/sync', methods=['GET'])
def sync() :
    obj_account = account()
    obj_tenant = tenant()
    obj_contact = contact()
    obj_session = app_session()
    obj_sfdc = sfdc()
    obj_one_garden = one_garden()

    if obj_sfdc.login() == True :
        # for adding sfdc tenant to tenants in db
        tenants = obj_sfdc.list_tenants()
        local_tenants = obj_tenant.list_tenants()
        exist_tenants = []
        for tenant1 in tenants :
            exist_tenants.append(tenant1['Name'])
            if tenant1['Name'] not in local_tenants :
                id = tenant1['attributes']['url'].split('/')[-1]
                obj_tenant.add_tenant(tenant1['Name'], id, tenant1['main_domain__c'], tenant1['Account_Name__c'], tenant1['environment_status__c'])

            # get other domains via one_garden to db
            domains = obj_one_garden.get_domains(tenant1['Name'])
            if domains != False :
                domains.remove(tenant1['main_domain__c'])
                obj_tenant.update_tenant_domains(tenant1['Name'], domains)

        # for deleting tenants in db not in sfdc
        for tenant1 in local_tenants :
            if tenant1 not in exist_tenants :
                obj_tenant.delete_tenant(tenant1)

        # get contract info via sfdc to db
        contracts = obj_sfdc.list_contracts()
        unique_contracts = {}
        for contract1 in contracts :
            if contract1['OneTenant__c'] in unique_contracts :
                if int(datetime.strptime(unique_contracts[contract1['OneTenant__c']]['contract_end_date__c'], '%Y-%m-%d').timestamp()) < int(datetime.strptime(contract1['contract_end_date__c'], '%Y-%m-%d').timestamp()) :
                    unique_contracts[contract1['OneTenant__c']] = contract1
            else :
                unique_contracts[contract1['OneTenant__c']] = contract1

        for contract1 in unique_contracts :
            tenant_info = obj_tenant.get_tenant_by_sfdc(contract1)
            if tenant_info != False :
                contract_data = {'end_date': unique_contracts[contract1]['contract_end_date__c'],
                                 'price': unique_contracts[contract1]['sub_total_price_sum__c'],
                                 'hac': unique_contracts[contract1]['hac_sum__c'],
                                 'hsb': unique_contracts[contract1]['hsb_sum__c'],
                                 'hdc': unique_contracts[contract1]['hdc_sum__c'],
                                 'dlp': unique_contracts[contract1]['dlp_sum__c'],
                                 'arc': unique_contracts[contract1]['archive_sum__c'],
                                 'hos': unique_contracts[contract1]['hos_sum__c']}
                obj_tenant.update_tenant_licenses(tenant_info['tenant_id'], contract_data)

        # for adding sfdc contacts to accounts in db
        contacts = obj_sfdc.list_contacts()
        local_contacts = obj_account.list_accounts()
        exist_contacts = []
        for contact1 in contacts :
            exist_contacts.append(contact1['Email'])
            id = contact1['attributes']['url'].split('/')[-1]
            if contact1['Email'] not in local_contacts :
                account_id = obj_account.add_account(id, contact1['Name'], contact1['Email'])
                account_data = {'phone': contact1['Phone']}
                obj_account.update_account(account_id, '', account_data)
            else :
                account_info = obj_account.get_account_by_email(contact1['Email'])
                account_data = {'phone': contact1['Phone']}
                obj_account.update_account(account_info['account_id'], '', account_data)

        # for deleting accounts in db not in sfdc contacts
        for contact1 in local_contacts :
            if contact1 not in exist_contacts :
                obj_account.delete_account(contact1)

        # for adding sfdc connects to contacts in db
        connects = obj_sfdc.list_connects()
        local_contacts = obj_account.list_accounts('sfdc')
        local_connects = obj_contact.list_contacts()
        exist_connects = []
        for connect in connects :
            if connect['Contact__c'] in local_contacts :
                account_info = local_contacts[connect['Contact__c']]
                connect_id = connect['attributes']['url'].split('/')[-1]
                exist_connects.append(connect_id)
                if connect_id in local_connects :
                    tenant1 = obj_tenant.get_tenant_by_sfdc(connect['OneTenant__c'])
                    contact_id = obj_contact.update_contact(connect_id, account_info['account_id'], tenant1['tenant_id'], connect['Distribution_Channel__c'], connect['support_flag__c'], connect['renewal_flag__c'], connect['emergency_flag__c'])
                else :
                    tenant1 = obj_tenant.get_tenant_by_sfdc(connect['OneTenant__c'])
                    contact_id = obj_contact.add_contact(connect_id, account_info['account_id'], tenant1['tenant_id'], connect['Distribution_Channel__c'], connect['support_flag__c'], connect['renewal_flag__c'], connect['emergency_flag__c'])

        # for deleting contacts in db not in sfdc connects
        for connect1 in local_connects :
            if connect1 not in exist_connects :
                obj_contact.delete_contact(connect1)

        return 'sync finished'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
