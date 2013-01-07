example: An sample project that uses ittybitty
****************************************

Here we will illustrate example project that utilizes ittybitty to expose
an application to the web. 

Lets consider the following simple application. It is a simple password store
that allows users to store their passwords in a central location and then get
them back. 

WARNING : This is a sample application and should not be used as an actual
password store.

Heres the inial code for the password store
.. highlight::

    #!/usr/bin/python
    import hashlib 
    import json
    import sys
    import os
    import getpass
    from Crypto.Cipher import AES
    
    BLOCK_SIZE = 32
    PADDING = "{"
    
    class passwordstore(object):
        def __init__(self, pwd_file, master_password):
            self.pwd_file = pwd_file
            key = hashlib.sha256(master_password).digest()
            self.encryptor = AES.new(key)
    
            self.user_data = {}
            if os.path.exists(pwd_file):
                self.read_pwd_file(pwd_file)
    
        def read_pwd_file(self, file):
            with open(file, "r") as f:
                data = f.read()
            if data:
                self.user_data = eval(data)
    
        def padd_pwd(self, pwd):
            return  pwd + (BLOCK_SIZE - len(pwd) % BLOCK_SIZE) * PADDING
    
        def get_password(self, username):
            if self.user_data.has_key(username):
                encrypted_password = self.user_data[username]
                return self.encryptor.decrypt(encrypted_password).rstrip(PADDING)
    
        def add_password(self, username, password):
            password = self.padd_pwd(password)
            self.user_data[username] = self.encryptor.encrypt(password)
    
        def close(self):
           with  open(self.pwd_file, "w") as f:
               f.write(str(self.user_data))
    
    if __name__ == "__main__":
        master_pass = getpass.getpass("Please enter master pwd\n")
        store = passwordstore("/tmp/foobax.pwd", master_pass)
        if sys.argv[1] == "add" :
            username = sys.argv[2]
            password = sys.argv[3]
            store.add_password(username, password)
        elif sys.argv[1] == "get" :
            username = sys.argv[2]
            print store.get_password(username)
        else:
            print "UNKNOWN option!"
        store.close()

As you can see this is a fairly simple application that stores credentials in a
file. Passwords are AES encrypted using a master_password. Lets see this app in
use::

    mercion@mwi-dev-II:/mwi/sandbox/password$ ./pwd.py add frank verner
    Please enter master pwd
    ****
    mercion@mwi-dev-II:/mwi/sandbox/password$ ./pwd.py get frank
    Please enter master pwd
    ****
    verner

As you can see this simple app already has one interface via the cmd line. But
woldnt it be awesome if we could access this app via the web so that we can use
this password store even when you are not logged in to same machine as the
password store.

This is were ittybitty comes in handy. Lets make the following changes :
1. Make the class passwordstore inherit from ittybitty
2. Add in some web faceing methods
3. Start the server.

Thats all their is to it so lets get started. Heres the new application ..


Now as you can see on line no X we have chanegd to base class for the
passwordstore. We have also add in a new function called web_get_pwd on line
number X. The  decorator on lin Y states tht this method is exposed via the web
api and '/get_pwd' is the path to this api method. When a HTTP GET request is
sent to /get_pwd the method on line X is called. The request that wsa made is
passed in to the method. Lines  x,y extract what the suername for that request
was and does a local lookup for that passowrd and returns it the the user.

Heres an example of this appication now accessed via the web ...



Thats all their is to it! Note that if you browse to '/help' you will get a list
off all the functions that are exposed via the web and their doc strings...

The same information is available via '/json-ref'...     


Now that we have out application exposed via the web wouldnt it be awsome if we
had some form of HTTP authentication enabled so that not just anyone could
browse your password store!

See part 2..    
    
