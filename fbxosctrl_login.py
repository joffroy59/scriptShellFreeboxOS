import requests
import simplejson as json
import hmac
import simplejson as json
from hashlib import sha1

class FreeboxOSCtrlLogin:
    def __init__(self, controler, fbxAddress, registrationCtrl, gAppDesc, log):
        self.isLoggedIn = False
        self.controler = controler 
        self.log = log
        self.gAppDesc = gAppDesc
        self.fbxAddress = fbxAddress
        self.registrationCtrl = registrationCtrl
        self.sessionToken = None
        
    def _login(self):
        """ Login to FreeboxOS using API credentials """
        self.log(">>> _login")
        if not self.isLoggedIn:
            if not self.registrationCtrl.isRegistered():
                raise FbxOSException("This app is not registered yet: you have to register it first!")
 
            # 1st stage: get challenge
            url = self.fbxAddress + "/api/v3/login/"
            # GET
            self.log("GET url: %s" % url)
            r = requests.get(url, timeout=3)
            self.log("GET response: %s" % r.text)
            # ensure status_code is 200, else raise exception
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Get error: %s" % r.text)
            # rc is 200 but did we really succeed?
            resp = json.loads(r.text)
            #self.log("Obj resp: %s" % resp)
            if resp['success']:
                if not resp['result']['logged_in']:
                    self.challenge = resp['result']['challenge']
            else:
                raise FbxOSException("Challenge failure: %s" % resp)
 
            # 2nd stage: open a session
            apptoken = self.registrationCtrl.registration['app_token']
            key = self.challenge
            self.log("challenge: " + key + ", apptoken: " + apptoken)
            # Encode to plain string as some python versions seem disturbed else (cf. issue#2)
            #if type(key) == unicode:
            key = key.encode()
			# Hashing token with key
            h = hmac.new(apptoken.encode(), key, sha1)
            password = h.hexdigest()
            url = self.fbxAddress + "/api/v3/login/session/"
            headers = {'Content-type': 'application/json',
                       'charset': 'utf-8', 'Accept': 'text/plain'}
            payload = {'app_id': self.gAppDesc['app_id'], 'password': password}
            #self.log("Payload: %s" % payload)
            data = json.dumps(payload)
            self.log("POST url: %s data: %s" % (url, data))
            # post it
            r = requests.post(url, data, headers=headers, timeout=3)
            # ensure status_code is 200, else raise exception
            self.log("POST response: %s" % r.text)
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Post response error: %s" % r.text)
            # rc is 200 but did we really succeed?
            resp = json.loads(r.text)
            #self.log("Obj resp: %s" % resp)
            if resp['success']:
                self.sessionToken = resp['result']['session_token']
                self.permissions = resp['result']['permissions']
                self.log("Permissions: %s" % self.permissions)
                if not self.permissions['settings']:
                    print("Warning: permission 'settings' has not been allowed yet \
in FreeboxOS server. This script may fail!")
            else:
                raise FbxOSException("Session failure: %s" % resp)
            self.isLoggedIn = True

    def _logout(self):
        """ logout from FreeboxOS NOT WORKING """
        # Not documented yet in the API
        self.log(">>> _logout DIASABLE BECAUSE NOT WORKING")
        """if self.isLoggedIn:
            url = self.fbxAddress + "/api/v3/login/logout/"
            log("self.sessionToken %s" % self.sessionToken)
            #headers = {
            #    'X-Fbx-App-Auth': self.sessionToken, 'Accept': 'text/plain'}
            # POST
            log("POST url: %s" % url)
            r = requests.post(url, timeout=3)
            log("POST response: %s" % r.text)
            # ensure status_code is 200, else raise exception
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Post error: %s" % r.text)
            # rc is 200 but did we really succeed?
            resp = json.loads(r.text)
            #log("Obj resp: %s" % resp)
            if not resp['success']:
                raise FbxOSException("Logout failure: %s" % resp)"""
        self.isLoggedIn = False

    def getSessionToken(self):
        return self.sessionToken
