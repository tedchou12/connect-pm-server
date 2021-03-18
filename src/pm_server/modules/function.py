from flask import session, render_template, request
import re
from .mail import mail
from .lang.ja import ja
from .lang.en import en
from .lang.zh import zh
from .config import config

def display_datetime(datetime='') :
    datetime = datetime

    return datetime

def display_name(name='') :
    name = name

    return name

def link(url='') :
    obj_config = config()
    return obj_config.params['hostname'] + url

def sendmail(recipient='', subject='', body='') :
    obj_mailer = mail()
    obj_config = config()

    subject = lang(subject)

    context = {'resources_path': obj_config.params['resources_path'],
               'val_addressee': recipient,
               'val_signature': lang('HENNGE Support'),
               'val_login': obj_config.params['hostname'],
               'link_home': obj_config.params['hostname'],
               'val_body': body,
               }

    body = render_template('mail.html', context=context)

    return obj_mailer.send(recipient, subject, body)

def lang(string='') :
    if 'lang' not in session :
        session['lang'] = 'en'
        supported_languages = ['en', 'ja', 'zh']
        session['lang'] = request.accept_languages.best_match(supported_languages)

    if session['lang'] == 'en' :
        obj_en = en()
        if string in obj_en.translations :
            return obj_en.translations[string]
    elif session['lang'] == 'zh' :
        obj_ja = zh()
        if string in obj_ja.translations :
            return obj_ja.translations[string]
    else :
        obj_ja = ja()
        if string in obj_ja.translations :
            return obj_ja.translations[string]

    return string

def display_number(number='') :
    if number != '' :
        number = number
    else :
        number = 0
    return '{0:,}'.format(int(number))

def check_password_strength(string='') :
    result = re.search('.{8,}', string)

    if result :
        return True
    else :
        return False
