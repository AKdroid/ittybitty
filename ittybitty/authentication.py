'''
A collection of Authentication handlers for itty-bitty.

The itty_bitty server calls an authentication handler to verify
the authentication credentials for each request. 

All authentication handlers must inherit from the base_authentication_handler.
'''

import ConfigParser
import pam
import logging
from ntlm import HTTPNtlmAuthHandler

log = logging.getLogger(__name__)


class base_authentication_handler:
    '''
    This is the base_authentication_handler that define all the required
    bound methods. 

    :param __author__: Defines who the author is. This is used for accounting
                      purposes.
    '''

    __author__ = 'built'

    def authenticate_credential(self, username, password):
        '''Called by server to authenticate credetials for each reuqest'''
        raise NotImplementedError()

    def add_credential(self, username, password):
        '''Used to add credentials'''
        raise NotImplementedError()

    def delete_credential(self, username):
        '''Used to delete credetials'''
        raise NotImplementedError()


class config_auth_handler(base_authentication_handler):
    '''
    This autentication will look for plain-text config
    file that has the following section...
    
    [Accounts]
    username1 = password1
    username2 = password2
    username3 = password3
    ..
    '''

    __author__ = 'built-in'

    def __init__(self, file_name):
        self.config = ConfigParser()
        self.config.read(file_name)

    @property
    def accounts(self):
        accounts  = {}
        for username in self.config.options("Accounts"):
            accounts["username"] = self.config.get("Accounts", username)
        return accounts

    def authenticate_credential(self, username, password):
        log.info("Attempting to authenticate user %s" %username)
        if accounts.has_key(username):
            if password == self.accounts[username] :
                log.info("Sucessfully Authenticated user %s" %username)
                return True
            else:
                log.warn("Incorect password for user %s." %username)
        else:
            log.warn("Failed to find user %s in Authentication db" %username)
            
        return False

    def add_credential(self, username, password):
        self.config.set("Accounts", username, password)

    def delete_credential(self, username):
        self.config.remove_option("Accounts", username)


class pam_auth_handler(base_authentication_handler):
    '''
    This authentication uses the Linux Plugable Authentication Module. This
    allows for itty to use the linux OS to handle authentication. 
    '''
    def authenticate_credential(self, username, password):
        log.info("Attempting to authenticate user %s" %user)
        if pam.authenticate(username, password):
            log.info("Sucessfully Authenticated user %s" %username)
            return True
        else:
            log.warn("Failed to Authenticate user %s" %username)
            return False

        


class ntlm_auth_handler(base_authentication_handler):

    def __init__(self, ntlm_server):
        self.ntlm_server = ntlm_server 

    def authenticate_credential(self, username, password):
        pass


class ldap_auth_handler(base_authentication_handler):
    pass
            






