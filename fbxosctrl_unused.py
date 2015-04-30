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
 