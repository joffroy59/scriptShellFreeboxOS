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

    def list_partition(self):
        """ List disk """
        self.log(">>> list_partition")
        self.controler._login()
        self.log("self.controler.sessionToken=%s" % self.controler.sessionToken)
        self.log("self.sessionToken=%s" % self.sessionToken)
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}
        
        url = self.fbxAddress + "/api/v3/storage/partition/"
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
            for part in resp['result']:
                print("* partId %s (%s)" % (part['id'],part['label']) )
                print("  - diskId %s" % (part['disk_id']) )    
                print(json.dumps(part, sort_keys=True, indent=4 * ' '))
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return isOn

    def _launchDiskCheckOn(self,partitionId,headers):
        """ launch check on one partition """
        self.log(">>> _launchDiskCheckOn %s " % partitionId)

        url = self.fbxAddress + "/api/v3/storage/partition/"+str(partitionId)+"/check"
        parameter = {'checkmode': 'ro'}
        # GET
        self.log("PUT url: %s" % url)
 
        r = requests.put(url, headers=headers, data=json.dumps(parameter), timeout=1)
        self.log("PUT response: %s" % r.text)
        
        # ensure status_code is 200, else raise exception
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Get error: %s" % r.text)
        # rc is 200 but did we really succeed?
        
        resp = json.loads(r.text)
        self.log("Obj resp: %s" % resp)
        
        #use response 
        isLaunch = False
        if True == resp['success']:
            isLaunch = True
        else:
            raise FbxOSException("Challenge failure: %s" % resp)

        return isLaunch
        
    def _checkDiskState(self,partitionId,headers):
        """ launch check of  disk on all disks"""
        self.log(">>> _checkDiskState")
        url = self.fbxAddress + "/api/v3/storage/partition/" + str(partitionId)
        
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
        isStateCheck = False
        if True == resp['success']:
            state = resp['result']['state']
            self.log("Partion id %s in state : %s" % (partitionId,state))
            isStateCheck = (state == 'checking')
            self.log('isStateCheck %s' % isStateCheck)
                    
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        return isStateCheck
        
        

    def check_partition_all(self):
        """ launch check of  disk on all disks"""
        self.log(">>> check_partition_all")
        
        self.controler._login()
        # GET Launch hdd check
        headers = {
            'X-Fbx-App-Auth': self.controler.sessionToken, 'Accept': 'text/plain'}        
        
        url = self.fbxAddress + "/api/v3/storage/partition/"
        
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
            for part in resp['result']:
                launched = False
                self.log(json.dumps(part, sort_keys=True, indent=4 * ' '))
                partId=part['id']
                
                launched=self._launchDiskCheckOn(partId,headers)
                if (launched):
                    launched = self._checkDiskState(partId,headers)
                    self.log("disk checking %s(check)" % launched)
                print("Partition Check%s Launch on Disk%s (partition %s)" % ("" if  launched else " not",part['disk_id'],partId))
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self.controler._logout()
        return isOn
