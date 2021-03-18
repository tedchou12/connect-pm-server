import json
import os
from .config import config
# from Crypto.Cipher import AES
from Crypto import Random
import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as PAD
import base64

class crypt :
    def __init__(self) :
        self.obj_config = config()
        self.key = b'dummyISalongstri'
        self.iv = b'dummyISalongstra'
        self.bs = 16
        self.crypto = AES.new(self.key, AES.MODE_CBC, self.iv)

    def encrypt(self, data='') :
        raw = self.pad(data)
        key = self.key
        iv = self.iv
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(cipher.encrypt(raw.encode('utf-8'))).decode('utf-8')

    def decrypt(self, data='') :
        return self.crypto.decrypt(data)

    def pad(self, s) :
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
