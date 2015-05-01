#! /usr/bin/env python

#import fbxosctrl_unused
import fbxosctrl_wifi as wifiMod
import fbxosctrl_registration as registrationMod
import fbxosctrl_login as loginCtrlMod
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
        self.challenge = None
        self.sessionToken = None
        self.permissions = None
        self.wifi = wifiMod.FreeboxOSCtrlWifi()
        self.registrationCtrl = registrationMod.FreeboxOSCtrlRegistration(appName,fbxAddress,log)
        self.storageCtrl = storageCtrlMod.FreeboxOSCtrlStorage(self,fbxAddress,log)
        self.login = loginCtrlMod.FreeboxOSCtrlLogin(self,fbxAddress,self.registrationCtrl,gAppDesc,log)
		
    def getWifiStatus(self):
        self.wifi.getWifiStatus(self,log)

    def _login(self):
        self.login._login()
        self.sessionToken = self.login.getSessionToken()
 
    def _logout(self):
        self.login._logout()
 

    def registerApp(self):
        self.registrationCtrl.registerApp()
 
    def list_disk(self):
        return self.storageCtrl.list_disk()

    def list_partition(self):
        return self.storageCtrl.list_partition()

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
        group.add_argument(
            '--list_partition', default=argparse.SUPPRESS, action='store_true', help='list partition')
        # Configure cmd=>callback association
        self.cmdCallbacks = {
            'registerapp': self.controller.registerApp,
            'wifistatus': self.controller.getWifiStatus,
            'list_disk': self.controller.list_disk,
            'list_partition': self.controller.list_partition,
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
