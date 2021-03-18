from flask import session
import json
import os
import pickle
import requests
import time
from .db import db
import random
import string
import hashlib

class contact :
    def __init__(self) :
        self.table = 'contact'
        self.account = {}
        self.dc_codes = {'end_user': {'code': 'エンドユーザ', 'label': 'End User'},
                         '1st_reseller': {'code': '1次店/請求リセラー', 'label': '1st Reseller'},
                         '2nd_partner': {'code': '2次店/導入リセラー', 'label': '2nd Reseller'},
                         '1st_partner_reseller': {'code': '1次店/導入リセラー/請求リセラー', 'label': 'Partner/Reseller'},
                         'vendor': {'code': '運用ベンダー', 'label': 'Vendor'},
                         'end': {'code': 'エンドユーザ扱い', 'label': 'End'}
                         }

    def list_contacts(self) :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + '')
        data = ()

        contacts = obj_database.select(query, data)
        results = {}
        for contact1 in contacts :
            results[contact1['contact_sfdc']] = contact1

        return results

    def add_contact(self, sfdc='', account_id='', tenant_id='', dc='', contact='', renew='', emergency='') :
        obj_database = db()
        query = ('INSERT INTO ' + self.table + ' (contact_sfdc, contact_account, contact_tenant, contact_dc, contact_contact, contact_renew, contact_emergency) VALUES (%s, %s, %s, %s, %s, %s, %s)')
        data = (sfdc, account_id, tenant_id, dc, contact, renew, emergency)

        return obj_database.insert(query, data)

    def update_contact(self, sfdc='', account_id='', tenant_id='', dc='', contact='', renew='', emergency='') :
        obj_database = db()
        query = ('UPDATE ' + self.table + ' SET contact_dc=%s, contact_contact=%s, contact_renew=%s, contact_emergency=%s WHERE contact_sfdc=%s AND contact_account=%s AND contact_tenant=%s')
        data = (dc, contact, renew, emergency, sfdc, account_id, tenant_id)

        return obj_database.update(query, data)

    def get_contact_by_sfdc(self, sfdc='') :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + ' WHERE contact_sfdc=%s')
        data = (sfdc, )

        contacts = obj_database.select(query, data)

        if len(contacts) > 0 :
            return contacts[0]
        else :
            return False

    def get_contacts_by_tenant(self, tenant_id='') :
        obj_database = db()

        # can only see contacts of the same dc
        query = ('SELECT * FROM ' + self.table + ' WHERE contact_tenant=%s AND contact_dc=%s')
        data = (tenant_id, session['contact']['contact_dc'])

        contacts = obj_database.select(query, data)

        if len(contacts) > 0 :
            return contacts
        else :
            return False

    def get_contacts_by_account(self, account_id='') :
        obj_database = db()

        if account_id == '' :
            account_id = session['account']['account_id']
        else :
            account_id = account_id

        # accessible permission
        query = ('SELECT * FROM ' + self.table + ' WHERE contact_account=%s AND ((contact_dc=%s AND contact_contact=%s) OR ((contact_dc=%s OR contact_dc=%s) AND (contact_contact=%s OR contact_renew=%s)) OR (contact_dc=%s AND contact_contact=%s AND contact_renew=%s))')
        data = (account_id, self.dc_codes['end_user']['code'], 1, self.dc_codes['1st_reseller']['code'], self.dc_codes['1st_partner_reseller']['code'], 1, 1, self.dc_codes['2nd_partner']['code'], 1, 0)

        contacts = obj_database.select(query, data)

        if len(contacts) > 0 :
            return contacts
        else :
            return []

    def check_contact_view_price(self, account_id='') :
        obj_database = db()

        if account_id == '' :
            account_id = session['account']['account_id']
        else :
            account_id = account_id

        # accessible permission
        query = ('SELECT * FROM ' + self.table + ' WHERE contact_account=%s AND contact_tenant=%s AND ((contact_dc=%s AND contact_contact=%s AND contact_renew=%s) OR ((contact_dc=%s OR contact_dc=%s) AND (contact_contact=%s OR contact_renew=%s)))')
        data = (account_id, session['tenant'], self.dc_codes['end_user']['code'], 1, 1, self.dc_codes['1st_reseller']['code'], self.dc_codes['1st_partner_reseller']['code'], 1, 1)

        contacts = obj_database.select(query, data)

        if len(contacts) > 0 :
            return True
        else :
            return False

    def delete_contact(self, id='') :
        obj_database = db()
        query = ('DELETE FROM ' + self.table + ' WHERE contact_sfdc=%s')
        data = (id, )

        return obj_database.delete(query, data)
