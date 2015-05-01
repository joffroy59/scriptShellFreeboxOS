#! /usr/bin/env python

#import fbxosctrl_unused
import fbxosctrl_wifi as wifiMod
import fbxosctrl_registration as registrationMod
import fbxosctrl_storage as storageCtrlMod

""" This utility handles some FreeboxOS commands which are sent to a
freebox server to be executed within FreeboxOS app.
Supported services:
- check wifi status
 
Note: once granted, this app must have 'settings' permissions set
to True in FreeboxOS webgui to be able to modify the configuration. """
 
import sys
import os
import argparse
import requests
import hmac
import simplejson as json
from hashlib import sha1

# fbxosctrl is a command line utility to get/set dialogs with FreeboxOS
#
# Copyright (C) 2013 Christophe Lherieau (aka skimpax)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
 
# FreeboxOS API is available here: http://dev.freebox.fr/sdk/os
 
 
########################################################################
# Configure parameters below on your own configuration
########################################################################
 
# your own password configured on your Freebox Server
#MAFREEBOX_PASSWD = '!0freebox0!'
 
# Set to True to enable logging to stdout
gVerbose = False

########################################################################
# Nothing expected to be modified below this line... unless bugs fix ;-)
########################################################################
 
FBXOSCTRL_VERSION = "1.0.0"
appName = os.path.basename(__file__)

__author__ = "Christophe Lherieau (aka skimpax) |  Jerome OFFROY"
__copyright__ = "Copyright 2013, Christophe Lherieau | Jerome OFFROY"
__credits__ = []
__license__ = "GPL"
__version__ = FBXOSCTRL_VERSION
__maintainer__ = "Jerome OFFROY"
__email__ = "jerome.offroy@gmail.com"
__status__ = "Production"

# Return code definitions
RC_OK = 0
 
# Descriptor of this app presented to FreeboxOS server to be granted
gAppDesc = {
    "app_id": "fr.freebox.%s.1" % appName,
    "app_name": "joffroy %s App 1" % appName,
    "app_version": "0.0.1",
    "device_name": "localExecutor"
}

def log(what):
    """ Log to stdout if verbose mode is enabled """
    if True == gVerbose:
        print(what)
 
 
class FbxOSException(Exception):
 
    """ Exception for FreeboxOS domain """
 
    def __init__(self, reason):
        self.reason = reason
 
    def __str__(self):
        return self.reason
 
 
class FreeboxOSCtrl:
 
    """ This class handles connection and dialog with FreeboxOS thanks to
its exposed REST API """
 
    def __init__(self, fbxAddress="http://mafreebox.freebox.fr"
                 ):
        """ Constructor """
        self.fbxAddress = fbxAddress
        self.isLoggedIn = False
        self.challenge = None
        self.sessionToken = None
        self.permissions = None
        self.wifi = wifiMod.FreeboxOSCtrlWifi()
        self.registrationCtrl = registrationMod.FreeboxOSCtrlRegistration(appName,fbxAddress,log)
        self.storageCtrl = storageCtrlMod.FreeboxOSCtrlStorage(self,fbxAddress,log)
		
    def getWifiStatus(self):
        self.wifi.getWifiStatus(self,log)

    def _login(self):
        """ Login to FreeboxOS using API credentials """
        log(">>> _login")
        if not self.isLoggedIn:
            if not self.registrationCtrl.isRegistered():
                raise FbxOSException("This app is not registered yet: you have to register it first!")
 
            # 1st stage: get challenge
            url = self.fbxAddress + "/api/v3/login/"
            # GET
            log("GET url: %s" % url)
            r = requests.get(url, timeout=3)
            log("GET response: %s" % r.text)
            # ensure status_code is 200, else raise exception
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Get error: %s" % r.text)
            # rc is 200 but did we really succeed?
            resp = json.loads(r.text)
            #log("Obj resp: %s" % resp)
            if resp['success']:
                if not resp['result']['logged_in']:
                    self.challenge = resp['result']['challenge']
            else:
                raise FbxOSException("Challenge failure: %s" % resp)
 
            # 2nd stage: open a session
            global gAppDesc
            apptoken = self.registrationCtrl.registration['app_token']
            key = self.challenge
            log("challenge: " + key + ", apptoken: " + apptoken)
            # Encode to plain string as some python versions seem disturbed else (cf. issue#2)
            #if type(key) == unicode:
            key = key.encode()
			# Hashing token with key
            h = hmac.new(apptoken.encode(), key, sha1)
            password = h.hexdigest()
            url = self.fbxAddress + "/api/v3/login/session/"
            headers = {'Content-type': 'application/json',
                       'charset': 'utf-8', 'Accept': 'text/plain'}
            payload = {'app_id': gAppDesc['app_id'], 'password': password}
            #log("Payload: %s" % payload)
            data = json.dumps(payload)
            log("POST url: %s data: %s" % (url, data))
            # post it
            r = requests.post(url, data, headers=headers, timeout=3)
            # ensure status_code is 200, else raise exception
            log("POST response: %s" % r.text)
            if requests.codes.ok != r.status_code:
                raise FbxOSException("Post response error: %s" % r.text)
            # rc is 200 but did we really succeed?
            resp = json.loads(r.text)
            #log("Obj resp: %s" % resp)
            if resp['success']:
                self.sessionToken = resp['result']['session_token']
                self.permissions = resp['result']['permissions']
                log("Permissions: %s" % self.permissions)
                if not self.permissions['settings']:
                    print("Warning: permission 'settings' has not been allowed yet \
in FreeboxOS server. This script may fail!")
            else:
                raise FbxOSException("Session failure: %s" % resp)
            self.isLoggedIn = True
 
    def _logout(self):
        """ logout from FreeboxOS NOT WORKING """
        # Not documented yet in the API
        log(">>> _logout DIASABLE BECAUSE NOT WORKING")
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
 

    def registerApp(self):
        self.registrationCtrl.registerApp()
 
    def list_disk(self):
        return self.storageCtrl.list_disk()

class FreeboxOSCli:
 
    """ Command line (cli) interpreter and dispatch commands to controller """
 
    def __init__(self, controller):
        """ Constructor """
        self.controller = controller
        # Configure parser
        self.parser = argparse.ArgumentParser(
            description='Command line utility to control some FreeboxOS services.')
        # CLI related actions
        self.parser.add_argument(
            '--version', action='version', version="%(prog)s " + __version__)
        self.parser.add_argument(
            '-v', action='store_true', help='verbose mode')
        # Real freeboxOS actions
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            '--registerapp', default=argparse.SUPPRESS, action='store_true',
            help='register this app to FreeboxOS (to be executed only once)')
        group.add_argument('--wifistatus', default=argparse.SUPPRESS,
                           action='store_true', help='get current wifi status')
        group.add_argument(
            '--list_disk', default=argparse.SUPPRESS, action='store_true', help='check list disk')
        # Configure cmd=>callback association
        self.cmdCallbacks = {
            'registerapp': self.controller.registerApp,
            'wifistatus': self.controller.getWifiStatus,
            'list_disk': self.controller.list_disk,
        }
 
    def cmdExec(self, argv):
        """ Parse the parameters and execute the associated command """
        args = self.parser.parse_args(argv)
        argsdict = vars(args)
        log("Args dict: %s" % argsdict)
        # Activate verbose mode if requested
        if True == argsdict['v']:
            global gVerbose
            gVerbose = True
        # Suppress '-v' command as not a FreeboxOS cmd
        del argsdict['v']
        # Let's execute FreeboxOS cmd
        return self.dispatch(argsdict.keys())
 
    def dispatch(self, args):
        """ Call controller action """
        for cmd in args:
            # retrieve callback associated to cmd and execute it, if not found
            # display help
            return self.cmdCallbacks.get(cmd, self.parser.print_help)()
 
 
if __name__ == '__main__':
        controller = FreeboxOSCtrl()
        cli = FreeboxOSCli(controller)
        rc = cli.cmdExec(sys.argv[1:])
        sys.exit(rc)
