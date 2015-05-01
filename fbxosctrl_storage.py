import requests
import simplejson as json

class FbxOSException(Exception):
 
    """ Exception for FreeboxOS domain """
 
    def __init__(self, reason):
        self.reason = reason
 
    def __str__(self):
        return self.reason

class FreeboxOSCtrlStorage:
    def __init__(self, controler, fbxAddress, log):
        self.controler = controler 
        self.log = log
        self.fbxAddress = fbxAddress
        self.sessionToken = None
    
    def setSessionToken(sessionToken):
        self.sessionToken = sessionToken

    def list_disk(self):
        """ List disk """
        self.log(">>> list_disk")
        self.controler._login()
        self.log("self.controler.sessionToken=%s" % self.controler.sessionToken)
        self.log("self.sessionToken=%s" % self.sessionToken)
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}
        
        url = self.fbxAddress + "/api/v3/storage/disk/"
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
            for disk in resp['result']:
                print("* diskId %s " % (disk['id']) )
                for part in disk['partitions']:
                    print("  - partId %s (%s)" % (part['id'],part['label']) )
                    
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return isOn
