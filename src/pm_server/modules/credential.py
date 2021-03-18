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

class credential :
    def __init__(self) :
        self.table = 'credential'
        self.account = {}

    def list_credentials(self) :
        obj_database = db()

        query = ('SELECT * FROM ' + self.table + ' WHERE credential_account=%s')
        data = (session['account']['account_id'], )

        credentials = obj_database.select(query, data)
        results = {}
        for credential in credentials :
            results[credential['credential_url']] = credential

        return results
