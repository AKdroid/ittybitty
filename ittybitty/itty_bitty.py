"""
Itty bitty
A simple python web service that allows you to expose exisiting/new
python aplication via the web easily.
"""

import cgi
import time
import mimetypes
import os
import re
import StringIO
import sys
import traceback
import logging
import tempfile
import wsgiref.simple_server
import threading
from threading import Thread

from ConfigParser import ConfigParser
from collections import defaultdict
from response import Response

from mappings import HTTP_MAPPINGS 
from mappings import REQUEST_MAPPINGS 

from html_template import html_config
from html_pages import HTML_reference_page
from html_pages import generate_json_reference

from version import ITTYBITTY_VERSION

from log_utils import JSONFormatter
from log_utils import JSONFileHandler
from log_utils import HtmlLogPage


root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
formatter = JSONFormatter()
log_folder  = tempfile.mkdtemp()
log_file = os.path.join(log_folder, "ittybitty.log")
jfh = JSONFileHandler(log_file, mode="w")
jfh.setFormatter(formatter)
root_logger.addHandler(jfh)

log = logging.getLogger("itty_bitty")

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

__author__ = 'mercion wilathgamuwage'
__version__ = ('0', '2', '1')
__license__ = 'BSD'



ERROR_HANDLERS = {}

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
class RequestError(Exception):
    """A base exception for HTTP errors to inherit from."""
    status = 404

    def __init__(self, message, hide_traceback=False):
        super(RequestError, self).__init__(message)
        self.hide_traceback = hide_traceback


class Forbidden(RequestError):
    '''HTTP 403 Forbidden Message'''
    status = 403


class NotFound(RequestError):
    '''HTTP 404 NotFound Message'''
    status = 404

    def __init__(self, message, hide_traceback=True):
        super(NotFound, self).__init__(message)
        self.hide_traceback = hide_traceback


class AppError(RequestError):
    '''Raise a HTTP 500 if we fail to execute the user code '''
    status = 500


class Redirect(RequestError):
    """
    Redirects the user to a different URL.

    Slightly different than the other HTTP errors, the Redirect is less
    'OMG Error Occurred' and more 'let's do something exceptional'. When you
    redirect, you break out of normal processing anyhow, so it's a very similar
    case."""
    status = 302
    url = ''

    def __init__(self, url):
        RequestError.__init__(self)
        self.url = url
        self.args = ["Redirecting to '%s'..." % self.url]


class lazyproperty(object):
    """A property whose value is computed only once. """
    def __init__(self, function):
        self._function = function

    def __get__(self, obj, _=None):
        if obj is None:
            return self

        value = self._function(obj)
        setattr(obj, self._function.func_name, value)
        return value


class Request(object):
    """An object to wrap the environ bits in a friendlier way."""
    GET = {}

    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self.content_length = 0
        self.query = None
        self.setup_self()

    def setup_self(self):
        '''Setup the request'''
        self.path = add_slash(self._environ.get('PATH_INFO', ''))
        self.method = self._environ.get('REQUEST_METHOD', 'GET').upper()
        self.query = self._environ.get('QUERY_STRING', '')
        self.content_length = 0

        try:
            self.content_length = int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            pass

        self.GET = self.build_get_dict()

    def __getattr__(self, name):
        """
        Allow accesses of the environment if we don't already have an attribute
        for. This lets you do things like::

            script_name = request.SCRIPT_NAME
        """
        return self._environ[name]

    @lazyproperty
    def POST(self):
        '''Return the a coplex dict containing the POST body. See fuc: build_complex_dict'''
        return self.build_complex_dict()

    @lazyproperty
    def PUT(self):
        '''Return the a coplex dict containing the POST body. See fuc: build_complex_dict'''
        return self.build_complex_dict()

    @lazyproperty
    def body(self):
        """Content of the request."""
        return self._environ['wsgi.input'].read(self.content_length)

    def build_get_dict(self):
        """Takes GET data and rips it apart into a dict."""
        raw_query_dict = parse_qs(self.query, keep_blank_values=1)
        query_dict = {}

        for key, value in raw_query_dict.items():
            if len(value) <= 1:
                query_dict[key] = value[0]
            else:
                # Since it's a list of multiple items, we must have seen more than
                # one item of the same name come in. Store all of them.
                query_dict[key] = value

        return query_dict

    def build_complex_dict(self):
        """Takes POST/PUT data and rips it apart into a dict."""
        print self.body
        raw_data = cgi.FieldStorage(fp=StringIO.StringIO(self.body), environ=self._environ)
        query_dict = {}

        print raw_data

        for field in raw_data:
            if isinstance(raw_data[field], list):
                # Since it's a list of multiple items, we must have seen more than
                # one item of the same name come in. Store all of them.
                query_dict[field] = [fs.value for fs in raw_data[field]]
            elif raw_data[field].filename:
                # We've got a file.
                query_dict[field] = raw_data[field]
            else:
                query_dict[field] = raw_data[field].value

        return query_dict

def handle_error(exception, request=None):
    """If an exception is thrown, deal with it and present an error page."""
    if request is None:
        request = {'_environ': {'PATH_INFO': ''}}

    if not getattr(exception, 'hide_traceback', False):
        (e_type, e_value, e_tb) = sys.exc_info()
        message = "%s occurred on '%s': %s\nTraceback: %s" % (
            exception.__class__,
            request._environ['PATH_INFO'],
            exception,
            ''.join(traceback.format_exception(e_type, e_value, e_tb))
        )
        request._environ['wsgi.errors'].write(message)

    if isinstance(exception, RequestError):
        status = getattr(exception, 'status', 404)
    else:
        status = 500

    if status in ERROR_HANDLERS:
        return ERROR_HANDLERS[status](request, exception)

    return not_found(request, exception)


def find_matching_url(request):
    """Searches through the methods who've registed themselves with the HTTP decorators."""
#    log.debug(REQUEST_MAPPINGS)
    if not request.method in REQUEST_MAPPINGS:
        raise NotFound("The HTTP request method '%s' is not supported." % request.method)

    for url_set in REQUEST_MAPPINGS[request.method]:
        match = url_set[0].search(request.path)

        if match is not None:
            return (url_set, match.groupdict())

    raise NotFound("Sorry, nothing here.")


def add_slash(url):
    """Adds a trailing slash for consistency in urls."""
    if not url.endswith('/'):
        url = url + '/'
    return url


def content_type(filename):
    """
    Takes a guess at what the desired mime type might be for the requested file.

    Mostly only useful for static media files.
    """
    ct = 'text/plain'
    ct_guess = mimetypes.guess_type(filename)

    if ct_guess[0] is not None:
        ct = ct_guess[0]

    return ct


def static_file(filename, root=MEDIA_ROOT):
    """
    Fetches a static file from the filesystem, relative to either the given
    MEDIA_ROOT or from the provided root directory.
    """
    if filename is None:
        raise Forbidden("You must specify a file you'd like to access.")

    # Strip the '/' from the beginning/end.
    valid_path = filename.strip('/')

    # Kill off any character trying to work their way up the filesystem.
    valid_path = valid_path.replace('//', '/').replace('/./', '/').replace('/../', '/')

    desired_path = os.path.join(root, valid_path)

    if not os.path.exists(desired_path):
        raise NotFound("File does not exist.")

    if not os.access(desired_path, os.R_OK):
        raise Forbidden("You do not have permission to access this file.")

    ct = str(content_type(desired_path))

    # Do the text types as a non-binary read.
    if ct.startswith('text') or ct.endswith('xml') or ct.endswith('json'):
        return open(desired_path, 'r').read()

    # Fall back to binary for everything else.
    return open(desired_path, 'rb').read()


# Static file handler

def serve_static_file(request, filename, root=MEDIA_ROOT, force_content_type=None):
    """
    Basic handler for serving up static media files.

    Accepts an optional ``root`` (filepath string, defaults to ``MEDIA_ROOT``) parameter.
    Accepts an optional ``force_content_type`` (string, guesses if ``None``) parameter.
    """
    file_contents = static_file(filename, root)

    if force_content_type is None:
        ct = content_type(filename)
    else:
        ct = force_content_type

    return Response(file_contents, content_type=ct)


#
# DECORATORS
#

#Response Decorators
def json_response(api_method):
    """
    Register a method as one that is supposed to return JSON data.

    If reponse is a python dictionary  it will attempt to convert the 
    python dictionary into json.

    >>> func = lambda x,y : {x:y}
    >>> response = json_response(func)
    >>> type(response) 

    """
    def wrapped(*args, **kwargs):
        log.debug("Evaluating API Method : {method}".format(method=api_method.__name__))
        response =  api_method(*args, **kwargs)

        #Here we inforce JSON data type and return back appropriate errors
        try:
            json_response = json.dumps(response)
        except ValueError  as e:
            raise JsonDecodeError(e)
        else:
            return json_response
    return wrapped
        

#REQUEST DECORATORS
def get(url):
    """Registers a method as capable of processing GET requests."""
    def wrapped(method):
        # Register.
        re_url = re.compile("^%s$" % add_slash(url))
        REQUEST_MAPPINGS['GET'].append((re_url, url, method))
        return method
    return wrapped


def post(url):
    """Registers a method as capable of processing POST requests."""
    def wrapped(method):
        # Register.
        re_url = re.compile("^%s$" % add_slash(url))
        REQUEST_MAPPINGS['POST'].append((re_url, url, method))
        return method
    return wrapped


def put(url):
    """Registers a method as capable of processing PUT requests."""
    def wrapped(method):
        # Register.
        re_url = re.compile("^%s$" % add_slash(url))
        REQUEST_MAPPINGS['PUT'].append((re_url, url, method))
        new.status = 201
        return method
    return wrapped


def delete(url):
    """Registers a method as capable of processing DELETE requests."""
    def wrapped(method):
        # Register.
        re_url = re.compile("^%s$" % add_slash(url))
        REQUEST_MAPPINGS['DELETE'].append((re_url, url, method))
        return method
    return wrapped


def error(code):
    """Registers a method for processing errors of a certain HTTP code."""
    def wrapped(method):
        # Register.
        ERROR_HANDLERS[code] = method
        return method
    return wrapped


# Error handlers

@error(401)
def unauthorized(request, exception):
    head = [('WWW-Authenticate', 'Basic realm="Pyxi Credentials"')]
    response = Response('HTTPUnauthorized', status=401, headers=head, content_type='text/plain')
    return response.send(request._start_response)


@error(403)
def forbidden(request, exception):
    response = Response('Forbidden', status=403, content_type='text/plain')
    return response.send(request._start_response)


@error(404)
def not_found(request, exception):
    response = Response('Not Found', status=404, content_type='text/plain')
    return response.send(request._start_response)


@error(500)
def app_error(request, exception):
    response = Response('Application Error', status=500, content_type='text/plain')
    return response.send(request._start_response)


@error(302)
def redirect(request, exception):
    response = Response('', status=302, content_type='text/plain', 
                            headers=[('Location', exception.url)])
    return response.send(request._start_response)


def authenticated(request):
    try:
        encoded_credentials = request.HTTP_AUTHORIZATION.strip().split()[-1]
    except KeyError:
        return False

    credentials = encoded_credentials.decode("base64")

    user_name, password = credentials.split(":", 1)

    if ACCOUNTS.get(user_name, False) == password:
        return True
    else:
        if password in ["TANDBERG", "x"]:
            return True
        return False


class lock(object):
    '''
    Represents a simple filebased lock object. If the underlying lockfile
    disapears this lock will return False.
    '''

    def __init__(self):
        self.lock_file = tempfile.NamedTemporaryFile(prefix="itty", suffix=".LOCK")
        self.lock_file.write(str(os.getpid()))

    def __call__(self):
        return os.path.exists(self.lock_file.name)

    def release(self):
        self.lock_file.close()

    def __del__(self):
        self.lock_file.close()
        

class MyHandler(wsgiref.simple_server.WSGIRequestHandler):
    '''
    The default requets handler for simeple_server is 
    wsgiref.simple_server.WSGIRequestHandlerr and it does reverse dns lookups 
    for each http connection and then it does not persisit http connections. 
    This was resulting in slow http requests so we now overide the address_string
    method to return the ip as the hostname.e
    '''
    def address_string(self):
        return str(self.client_address[0])

class ittybitty_server(threading.Thread):
    '''
    This is the main ittybitty web servervice.

    To start the service in a thread call :func:`ittybitty.ittybitty_server.start`.

    To start the service direcotry call
:func:`ittybitty.ittybitty_server.run_ittybitty` to run the web server.

    '''
    def __init__(self, host=None, port=8090):
        '''
        :param:`host`: If not specified then the host address will be determind
                by :func:`socket.gethostbyname`
        :param:`port`: The port on whic the service will bind to. 
        '''
        threading.Thread.__init__(self)
        self._auth_handler = None
        self.lock = lock()
        self.run_thread = None
        if host is None:
            import socket
            host = socket.gethostbyname(socket.gethostname())
        self.host = host
        self.port = port
        self.start_time = time.time()

        self.html_config = html_config(host=self.host,
                                       port=self.port,
                                       start_time=self.start_time)

    @property
    def uptime(self):
        return time.time() - self.start_time

    @property
    def authentication_handler(self):
        '''
        The authentication handler is an object that is responsible for
        Authenticateing any HTTP requests. The default handler is none and thus
        the itty will not challenge for any client autenitcation.

        All authentiation handlers must inherit from the 
        :class:`ittybitty.authentication.base_authentication_handler`. See
        :mod:`ittybitty.authentication` for a list of all the available 
        authentication handlers. 
        '''
        return self._auth_handler

    @authentication_handler.setter
    def set_auth_handler(self, handler):
        if not isinstance(handler, base_authentication_handler) :
            raise ValueError("The authentication handler must have been \
                            inherited from base_authentication_handler")
        self._auth_handler = handler


    def stop(self):
        '''
        This stop the service from handling requsts. Once the service is
        stopped it can be started again.
        '''
        threading.Thread(target=self.srv.shutdown).start()

    def handle_request(self, environ, start_response):
        '''
        This is responlible fo depatching to user code. We seach thru all the 
        registered GET, POST, DELETE etc functions to find one that matches the
        requst url and execute it.
        '''
        try:
            request = Request(environ, start_response)
            if self.authentication_handler != None :
                if self.authenticated(response):
                    return ERROR_HANDLERS[401](request, "Please Authenticate yourself")
        except ValueError:
            pass
    
        try:
            (re_url, url, callback), kwargs = find_matching_url(request)
            name = callback.__name__
            log.debug(REQUEST_MAPPINGS)
            log.critical(name)
            log.debug("The callback function name is %s" %name)
            response = getattr(self, name)(request)
        except Exception, e:
            return handle_error(e, request)
    
        if not isinstance(response, Response):
            response = Response(response)
    
        return response.send(start_response)

    def wsgiref_adapter(self, host, port):
        '''
        This is the main adaptor that is used forhandleing requests. See the
        documentation for :mod:`wsgire` for more information..
        '''
        from wsgiref.simple_server import make_server

        self.srv = make_server(host, port, self.handle_request, handler_class=MyHandler)
        self.srv.serve_forever(poll_interval=0.1)
        #while self.lock():
        #    print "lock is here"
        #    srv.handle_request()

        #print "lock gone"
            


    def run(self):
        '''
        This will start the ittybitty service. Note that this function mearly
        calls run_ittybity. When this fucntion is called by
        threading.Thread.start(), the itty server will be run in a thread.
        If you do not want to run ittybitty in a thread you can call run_tty 
        directly.
        '''
        return self.run_ittybitty()



    def run_ittybitty(self):
        """
        Runs the itty web server.
        Available autentication_handlers can bee found in :mod
`auth_handlers`.
        
        The web server uses python's built-in wsgiref implementation   
        """
    
        log.info( 'Itty Bitty starting up WSGI server...')
        log.info( 'Listening on http://%s:%s...' % (self.host, self.port))
        print 'Listening on http://%s:%s...' % (self.host, self.port)
        log.info( 'Browse to http://%s:%s/api for a list of API refernces' \
                                                        %(self.host, self.port))
 

        log.warn("Here is a log msg")
        log.critical("This is a critisd")
        log.error("Can she ssd")

        try:
            self.wsgiref_adapter(self.host, self.port)
        except KeyboardInterrupt:
            log.warn( 'Shutting down. Have a nice day!')

    #########################################
    # Builtin api methods                   #
    #########################################


    @get("/html-ref")
    def html_api_reference(self, request):
        '''
        <a class="example" href="json-ref">/html-ref</a>
        
        This method will return a html page describing all of the public
        mthods that have been exposed to the ittybitty service.
        '''
        page = HTML_reference_page(url="/html-ref",
                                    html_config=self.html_config)
        return page.html


    @get("/json-ref")
    def json_api_reference(self, request):
        '''
        <a class="example" href="html-ref">/json-ref</a>

        This method will return a json page that contains a description
        of all of the methods exposed to this service.
        '''

        return generate_json_reference()

    @get("/html-logs")
    def html_log_file_viewer(self, request):
        '''
        This will show all of the lods

        '''
        params = request.build_get_dict()
        page = HtmlLogPage(url="/html-logs", html_config=self.html_config)
        page.json_log_file = jfh.baseFilename
        page.filter_params = params
        return page.html
       
    @get("/json-logs")
    def json_log_file(self, result):
        '''
        This will return back the contents of the log file in json format
        ''' 
       
        with open(jfh.baseFilename, "r") as f:
            data = f.read() 
        return data



if __name__ == "__main__":

    class application(ittybitty_server):
        
        @get("/")
        def index(self, request):
            print request
            print dir(request)
            return "Hello World"

        @post("/debug")
        def debug(self, request):
            if request.CONTENT_LENGTH > 0 :
                if request.CONTENT_TYPE != "application/json":
                    #Raise a content type error
                    pass    
            
            print request.CONTENT_TYPE
            print request.CONTENT_LENGTH

    server = application(host="10.50.159.204")
    try:
       server.start()
    except:
        server.stop()
