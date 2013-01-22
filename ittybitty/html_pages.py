from html_template import basepage

from mappings import REQUEST_MAPPINGS
from version import ITTYBITTY_VERSION
from docstring_utils import decode_docstring
import json 
#from html_templares.css import css_main 

ref_page_js = '''
<script>                                                                        
function rawPost(url, tid)                                                      
{                                                                               
                                                                                
    $.ajax(url,                                                                 
    {                                                                           
      'data':document.getElementById(tid).value,                                
      'type':"POST",                                                            
      'processData': false,                                                     
      'contentType':'application/json'                                          
    });                                                                         
  };                                                                            
</script>
'''

class HTML_reference_page(basepage):

    def __init__(self, *args, **kwargs):
        basepage.__init__(self, *args, **kwargs)

        self.header = '''
        <script src="http://code.jquery.com/jquery-latest.min.js"
        type="text/javascript"></script>'''
        self.header += ref_page_js 

        json_ref = generate_json_reference()
        json_ref = kwargs.get("json_ref", generate_json_reference())
        ref = json.loads(json_ref)
    
        self.body += '''<div id="secondary_header">
            <H1> ittybitty REQUEST_MAPPINGS Reference </H1>
            <p> A Table of all of the methods that have been exposed to the ittybitty
            service. This same information is available in json format on <a\
            href="/ref-json">/ref-json</a>.</p>
            </div>'''
        
        table = '''
        <table id="apiref">
        <tr>
            <th> ID </th>
            <th> Method </th>
            <th> Name </th>
            <th> Path </th>
            <th> Documentation </th>
            <th> Example </th>
        </tr>'''
        for api in ref:
            html, forms = decode_docstring(api["doc"],api["path"], api["method"])
            print html
            if " ".join(forms).strip() == '':
                forms = ['''<input type="submit" class="button" onclick='window.open("%s")' />'''
%api["path"]]
            row = '''
            <tr>
                <td> {id} </td>
                <td> {method} </td>
                <td> {name} </td>
                <td> <a href="{path_link}">{path}</a></td>
                <td style="text-align:left;"> {html} </td>
                <td width="350px"> {form} </td>
            </tr>'''.format( path_link = api["path"][1:],
                             html = html,
                             form = "</hr>".join(forms), **api)
            table += row
        table += '</table>'
        self.body += table



def generate_json_reference(REQUEST_MAPPINGS=REQUEST_MAPPINGS):
    mappings_list = []
    for method in REQUEST_MAPPINGS.keys():
        for regex, path, function in REQUEST_MAPPINGS[method]:
            mapping = dict()
            mapping["name"] = function.__name__
            mapping["doc"] = function.func_doc
            mapping["path"] = path
            mapping["method"] = method
            mapping["id"] = id(function)
            mapping["example"] = "NotImplemented"
            
            mappings_list.append(mapping)
    return json.dumps(mappings_list)




