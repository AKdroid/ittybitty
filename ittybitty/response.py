'''
A module containing all HTTP response related methods
'''

import logging
import json


from mappings import HTTP_MAPPINGS
from mappings import REQUEST_MAPPINGS

log = logging.getLogger(__name__)

class Response(object):
    '''
    A HTTP resonse that build up the :arg `status` and :arg `headers`.

    :class `itty_server.handler_request` builds a Resoponse from all 
    the api calls. 

    '''
    headers = []

    def __init__(self, output, headers=None, status=200, content_type='text/html'):
        self.output = output
        self.content_type = content_type
        self.status = status
        self.headers = []

        if headers and isinstance(headers, list):
            self.headers = headers

    def add_header(self, key, value):
        '''
        Add a headder to the response request.
        '''
        self.headers.append((key, value))

    def send(self, start_response):
        '''Sends response t client '''
        status = "%d %s" % (self.status, HTTP_MAPPINGS.get(self.status))
        headers = [('Content-Type', "%s; charset=utf-8" % self.content_type)] + self.headers
        final_headers = []

        # Because Unicode is unsupported...
        for header in headers:
            final_headers.append((self.convert_to_ascii(header[0]), self.convert_to_ascii(header[1])))

        start_response(status, final_headers)

        if isinstance(self.output, unicode):
            return self.output.encode('utf-8')
        else:
            return self.output

    def convert_to_ascii(self, data):
        '''Encode data as us-ascii'''
        if isinstance(data, unicode):
            try:
                return data.encode('us-ascii')
            except UnicodeError, e:
                raise
        else:
            return str(data)


def xml_response(api_method):
    """
    Register a method as one that is supposed to return XML data

    An API decorated with this function will only return XML
    data. It will create a :class `Response` with a content_type = "text/xml".

    Data can defined as a nested dictionary and :func `xml_response` will
    automatically try to encode it into xml.

    """
    raise NotImplementedError()




def json_response(api_method):
    """ 
    Register a method as one that is supposed to return JSON data.

    An API decorated with this function will only return JSON
    data. It will create a :class `Response` with a content_type = "text/json".

    If reponse is a python dictionary  it will attempt to convert the 
    python dictionary into :class `json`.

    >>> import json
    >>> func = lambda x,y : {x:y}
    >>> response = json_response(func)("a", "b")
    >>> json.loads(response) == {"a":"b"}
    True

    Example Usage :

    @json_response
    @get("/sample")
    def test(request):
        return None

    """
    def wrapped(*args, **kwargs):
        log.debug("Evaluating API Method : {method}".format(method=api_method.__name__))
        response =  api_method(*args, **kwargs)


        #Here we inforce JSON data type and return back appropriate errors
        try:
            json_response = json.dumps(response)
        except ValueError  as e:
            raise ValueError(e)
        else:
            #Build a JSON Response
            return Response(json_response, content_type="json/text")
    return wrapped



if __name__ == "__main__":
    import doctest
    doctest.testmod()
