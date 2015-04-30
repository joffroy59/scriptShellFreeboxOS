RC_WIFI_OFF = 0
RC_WIFI_ON = 1

    def reboot(self):
        """ Reboot the freebox server now! """
        log(">>> reboot")
        self._login()
        headers = {'X-Fbx-App-Auth': self.sessionToken, 'Accept': 'text/plain'}
        url = self.fbxAddress + "/api/v3/system/reboot/"
        # POST
        log("POST url: %s" % url)
        r = requests.post(url, headers=headers, timeout=3)
        log("POST response: %s" % r.text)
        # ensure status_code is 200, else raise exception
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Post error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(b'%s' % r.text)
        #log("Obj resp: %s" % resp)
        if not resp['success']:
            raise FbxOSException("Logout failure: %s" % resp)
        print("Freebox Server is rebooting")
        self.isLoggedIn = False
        return True
 
    def _setWifiStatus(self, putOn):
        """ Utility to activate or deactivate wifi radio module """
        log(">>> _setWifiStatus")
        self._login()
        # PUT wifi status
        headers = {'X-Fbx-App-Auth': self.sessionToken, 'Accept': 'text/plain'}
        if putOn:
            data = {'ap_params': {'enabled': True}}
        else:
            data = {'ap_params': {'enabled': False}}
        url = self.fbxAddress + "/api/v2/wifi/config/"
        log("PUT url: %s data: %s" % (url, json.dumps(data)))
        # PUT
        try:
            r = requests.put(url, data=json.dumps(data), headers=headers, timeout=1)
            log("PUT response: %s" % r.text)
        except requests.exceptions.Timeout as timeoutExcept:
            if not putOn:
                # If we are connected using wifi, disabling wifi will close connection
                # thus PUT response will never be received: a timeout is expected
                print("Wifi is now OFF")
                return 0
            else:
                # Forward timeout exception as should not occur
                raise timeoutExcept
        # Response received
        # ensure status_code is 200, else raise exception
        if requests.codes.ok != r.status_code:
            raise FbxOSException("Put error: %s" % r.text)
        # rc is 200 but did we really succeed?
        resp = json.loads(b'%s' % r.text)
        #log("Obj resp: %s" % resp)
        isOn = False
        if True == resp['success']:
            if resp['result']['ap_params']['enabled']:
                print("Wifi is now ON")
                isOn = True
            else:
                print("Wifi is now OFF")
        else:
            raise FbxOSException("Challenge failure: %s" % resp)
        self._logout()
        return isOn

    def setWifiOn(self):
        """ Activate (turn-on) wifi radio module """
        log(">>> setWifiOn")
        return self._setWifiStatus(True)
 
    def setWifiOff(self):
        """ Deactivate (turn-off) wifi radio module """
        log(">>> setWifiOff")
        return self._setWifiStatus(False)
