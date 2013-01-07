from html_template import basepage

from mappings import REQUEST_MAPPINGS
from version import ITTYBITTY_VERSION

import json 
#from html_templares.css import css_main 


class HTML_reference_page(basepage):

    def __init__(self, *args, **kwargs):
        basepage.__init__(self, *args, **kwargs)

        json_ref = generate_json_reference()
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
            row = '''
            <tr>
                <td> {id} </td>
                <td> {method} </td>
                <td> {name} </td>
                <td> <a href="{path_link}">{path}</a></td>
                <td> {doc} </td>
                <td> {example} </td>
            </tr>'''.format( path_link = api["path"][1:], **api)
            table += row
        table += '</table>'
        self.body += table



def generate_json_reference():
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




