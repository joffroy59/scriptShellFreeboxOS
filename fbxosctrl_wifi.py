#! /usr/bin/env python
import requests
import simplejson as json

class FreeboxOSCtrlWifi:

    def getWifiStatus(self,controler,log):
        """ Get the current status of wifi: 1 means ON, 0 means OFF """
        log(">>> getWifiStatus")
        controler._login()
        # GET wifi status
        headers = {
            'X-Fbx-App-Auth': controler.sessionToken, 'Accept': 'text/plain'}
        url = controler.fbxAddress + "/api/v2/wifi/ap/0"
        # GET
        log("GET url: %s" % url)
        r = requests.get(url, headers=headers, timeout=1)
        #log("GET response: %s" % r.text)
        # ensure status_code is 200, else raise exception
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Get error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(r.text)
        #log("Obj resp: %s" % resp)
        isOn = True
        if True == resp['success']:
            if resp['result']['status']['state']=='active':
                print("Wifi is ON")
                isOn = True
            else:
                print("Wifi is OFF")
                isOn = False
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        controler._logout()
        return isOn

