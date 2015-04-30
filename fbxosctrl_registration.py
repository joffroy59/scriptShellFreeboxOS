#! /usr/bin/env python
import simplejson as json
import os
import requests

class FreeboxOSCtrlRegistration:

    def __init__(self, appName, fbxAddress, log):
         
        self.registration = {'app_token': '', 'track_id': None}
        self.registrationSaveFile = "%s_registration.app_token" % (appName)
        self.log = log
        self._loadRegistrationParams()
        self.fbxAddress = fbxAddress
        
    def _saveRegistrationParams(self):
        """ Save registration parameters (app_id/token) to a local file """
        self.log(">>> _saveRegistrationParams")
        with open(self.registrationSaveFile, 'w') as outfile:
            json.dump(self.registration, outfile)
 
    def _loadRegistrationParams(self):
        self.log(">>> _loadRegistrationParams")
        if os.path.exists(self.registrationSaveFile):
            with open(self.registrationSaveFile) as infile:
                self.registration = json.load(infile)

    def registerApp(self):
        """ Register this app to FreeboxOS to that user grants this apps via Freebox Server
LCD screen. This command shall be executed only once. """
        self.log(">>> registerApp")
        register = True
        if self.hasRegistrationParams():
            status = self.getRegistrationStatus()
            if 'granted' == status:
                print("This app is already granted on Freebox Server (app_id = %s). You can now dialog with it." % self.registration['track_id'])
                register = False
            elif 'pending' == status:
                print("This app grant is still pending: user should grant it on Freebox Server lcd/touchpad (app_id = %s)." % self.registration['track_id'])
                register = False
            elif 'unknown' == status:
                print("This app_id (%s) is unknown by Freebox Server: you have to register again to Freebox Server to get a new app_id." % self.registration['track_id'])
            elif 'denied' == status:
                print("This app has been denied by user on Freebox Server (app_id = %s)." % self.registration['track_id'])
                register = False
            elif 'timeout' == status:
                print("Timeout occured for this app_id: you have to register again to Freebox Server to get a new app_id (current app_id = %s)." % self.registration['track_id'])
            else:
                print("Unexpected response: %s" % status)
 
        if register:
            global gAppDesc
            url = self.fbxAddress + "/api/v3/login/authorize/"
            data = json.dumps(gAppDesc)
            headers = {
                'Content-type': 'application/json', 'Accept': 'text/plain'}
            # post it
            self.log("POST url: %s data: %s" % (url, data))
            r = requests.post(url, data=json.dumps(gAppDesc), headers=headers, timeout=3)
            self.log("POST response: %s" % r.text)
            # ensure status_code is 200, else raise exception
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Post error: %s" % r.text)
            # rc is 200 but did we really succeed?
            self.log("r.text = %s" % r.text)
            resp = json.loads(r.text)
            self.log("Obj resp: %s" % resp)
            if True == resp['success']:
                self.registration['app_token'] = resp['result']['app_token']
                self.registration['track_id'] = resp['result']['track_id']
                self._saveRegistrationParams()
                print("Now you have to accept this app on your Freebox server: take a look on its lcd screen.")
            else:
                print("NOK")

    def hasRegistrationParams(self):
        """ Indicate whether registration params look initialized """
        self.log(">>> hasRegistrationParams")
        return None != self.registration['track_id'] and '' != self.registration['app_token']

    def getRegistrationStatus(self):
        """ Get the current registration status thanks to the track_id """
        self.log(">>> getRegistrationStatus")
        if self.hasRegistrationParams():
            url = self.fbxAddress + \
                "/api/v3/login/authorize/%s" % self.registration['track_id']
            self.log(url)
            # GET
            self.log("GET url: %s" % url)
            r = requests.get(url, timeout=3)
            self.log("GET response: %s" % r.text)
            # ensure status_code is 200, else raise exception
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Get error: %s" % r.text)
            resp = json.loads(r.text)
            return resp['result']['status']
        else:
            return "Not registered yet!"

    def isRegistered(self):
        """ Check that the app is currently registered (granted) """
        self.log(">>> isRegistered")
        if self.hasRegistrationParams() and 'granted' == self.getRegistrationStatus():
            return True
        else:
            return False
 