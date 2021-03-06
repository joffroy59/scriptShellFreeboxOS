import requests
import simplejson as json

class FbxOSException(Exception):
 
    """ Exception for FreeboxOS domain """
 
    def __init__(self, reason):
        self.reason = reason
 
    def __str__(self):
        return self.reason

class FreeboxOSCtrlAirmedia:
    def __init__(self, controler, fbxAddress, log):
        self.controler = controler 
        self.log = log
        self.fbxAddress = fbxAddress
        self.sessionToken = None
    
    def setSessionToken(sessionToken):
        self.sessionToken = sessionToken

    def server_status(self):
        """ server status """
        self.log(">>> server_status")
        self.controler._login()
        self.log("self.controler.sessionToken=%s" % self.controler.sessionToken)
        self.log("self.sessionToken=%s" % self.sessionToken)
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}
        
        url = self.fbxAddress + "/api/v3/airmedia/config/"
        # GET
        self.log("GET url: %s" % url)
        r = requests.get(url, headers=headers, timeout=1)
        self.log("GET response: %s" % r.text)
        
        # ensure status_code is 200, else raise exception
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Get error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(r.text)
        self.log("Obj resp: %s" % resp)
        
        #use response 
        enable = False
        if True == resp['success']:
            enable = resp['result']['enabled']
            print("server air media enable: %s" % enable)
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return enable

    def list_airmedia(self):
        """ List airmedia """
        self.log(">>> list_airmedia")
        self.controler._login()
        self.log("self.controler.sessionToken=%s" % self.controler.sessionToken)
        self.log("self.sessionToken=%s" % self.sessionToken)
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}
        
        url = self.fbxAddress + "/api/v3/airmedia/receivers/"
        # GET
        self.log("GET url: %s" % url)
        r = requests.get(url, headers=headers, timeout=1)
        self.log("GET response: %s" % r.text)
        
        # ensure status_code is 200, else raise exception
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Get error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(r.text)
        self.log("Obj resp: %s" % resp)
        
        #use response 
        isOn = True
        if True == resp['success']:
            for device in resp['result']:
                print("* device %s (secured %s)" % (device['name'], device['password_protected']) )
                for capability in device['capabilities']:
                    print("\t- %s " % (capability) )
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return isOn

    def airmedia_play(self, receiver_name, mediaUrl):
        """ airmedia_play """
        self.log(">>> airmedia_play")
        self.controler._login()
        self.log("self.controler.sessionToken=%s" % self.controler.sessionToken)
        self.log("self.sessionToken=%s" % self.sessionToken)
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}
        
        url = self.fbxAddress + "/api/v3/airmedia/receivers/"+ receiver_name + "/" 
        # GET
        self.log("POST url: %s" % url)
        postData = {"action": "start", "media_type": "video","media": mediaUrl}
        data = json.dumps(postData)
        self.log("POST url: %s data: %s" % (url, data))
        # post it
        r = requests.post(url, data, headers=headers, timeout=3)
        # ensure status_code is 200, else raise exception
        self.log("POST response: %s" % r.text)
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Post response error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(r.text)
        #log("Obj resp: %s" % resp)

        #use response 
        isOn = resp['success']
        if True == isOn:
            self.log("launch airplay")
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return isOn

    def airmedia_stop(self, receiver_name):
        """ airmedia_stop """
        self.log(">>> airmedia_stop")
        self.controler._login()
        self.log("self.controler.sessionToken=%s" % self.controler.sessionToken)
        self.log("self.sessionToken=%s" % self.sessionToken)
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}
        
        url = self.fbxAddress + "/api/v3/airmedia/receivers/"+ receiver_name + "/" 
        # GET
        self.log("POST url: %s" % url)
        postData = {"action": "stop", "media_type": "video"}
        data = json.dumps(postData)
        self.log("POST url: %s data: %s" % (url, data))
        # post it
        r = requests.post(url, data, headers=headers, timeout=3)
        # ensure status_code is 200, else raise exception
        self.log("POST response: %s" % r.text)
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Post response error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(r.text)
        #log("Obj resp: %s" % resp)

        #use response 
        isOn = resp['success']
        if True == isOn:
            self.log("stop airplay")
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return isOn

