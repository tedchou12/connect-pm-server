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

class tenant :
    def __init__(self) :
        self.table = 'tenant'
        self.link_table = 'account_tenant'
        self.account = {}
        self.reset_duration = 60 * 60 * 24 * 2

    def list_tenants(self) :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + '')
        data = ()

        tenants = obj_database.select(query, data)
        results = {}
        for tenant1 in tenants :
            results[tenant1['tenant_id']] = tenant1

        return results

    def add_tenant(self, id='', sfdc='', domain='', name='', status='') :
        obj_database = db()
        query = ('INSERT INTO ' + self.table + ' (tenant_id, tenant_sfdc, tenant_domain, tenant_name, tenant_status) VALUES (%s, %s, %s, %s, %s)')
        data = (id, sfdc, domain, name, status)

        return obj_database.insert(query, data)

    def update_tenant_domains(self, id='', domains=[]) :
        obj_database = db()
        query = ('UPDATE ' + self.table + ' SET tenant_domains=%s WHERE tenant_id=%s')
        data = (json.dumps(domains), id)

        if obj_database.update(query, data) == True :
            return True
        else :
            return False

    def update_tenant_licenses(self, id='', licenses={}) :
        obj_database = db()
        query = ('UPDATE ' + self.table + ' SET tenant_licenses=%s WHERE tenant_id=%s')
        data = (json.dumps(licenses), id)

        if obj_database.update(query, data) == True :
            return True
        else :
            return False

    def get_tenant(self, id='') :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + ' WHERE tenant_id=%s')
        data = (id, )

        tenants = obj_database.select(query, data)

        if len(tenants) > 0 :
            tenant1 = tenants[0]
            if 'tenant_domains' not in tenants[0] or tenants[0]['tenant_domains'] == None or tenants[0]['tenant_domains'] == '' :
                tenant1['tenant_domains'] = []
            else :
                tenant1['tenant_domains'] = json.loads(tenants[0]['tenant_domains'])
            if 'tenant_licenses' not in tenants[0] or tenants[0]['tenant_licenses'] == None or tenants[0]['tenant_licenses'] == '' :
                tenant1['tenant_licenses'] = {}
            else :
                tenant1['tenant_licenses'] = json.loads(tenants[0]['tenant_licenses'])

            return tenant1
        else :
            return False

    def get_tenant_by_sfdc(self, id='') :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + ' WHERE tenant_sfdc=%s')
        data = (id, )

        tenants = obj_database.select(query, data)

        if len(tenants) > 0 :
            tenant1 = tenants[0]
            if 'tenant_domains' not in tenants[0] or tenants[0]['tenant_domains'] == None or tenants[0]['tenant_domains'] == '' :
                tenant1['tenant_domains'] = []
            else :
                tenant1['tenant_domains'] = json.loads(tenants[0]['tenant_domains'])
            if 'tenant_licenses' not in tenants[0] or tenants[0]['tenant_licenses'] == None or tenants[0]['tenant_licenses'] == '' :
                tenant1['tenant_licenses'] = {}
            else :
                tenant1['tenant_licenses'] = json.loads(tenants[0]['tenant_licenses'])

            return tenant1
        else :
            return False

    def tenant_id2domain(self, id='') :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + ' WHERE tenant_id=%s')
        data = (id, )

        tenants = obj_database.select(query, data)

        if len(tenants) > 0 :
            return tenants[0]['tenant_domain']
        else :
            return False

    def delete_tenant(self, id='') :
        obj_database = db()
        query = ('DELETE FROM ' + self.table + ' WHERE tenant_id=%s')
        data = (id, )

        return obj_database.delete(query, data)
