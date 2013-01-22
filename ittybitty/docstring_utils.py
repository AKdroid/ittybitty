#import locale
import pkg_resources
#locale.setlocale(locale.LC_ALL, 'en_gb.en_gb')
#locale.setlocale(locale.LC_ALL, 'de_DE')
import re
from docutils import core, io


def html_parts(input_string, source_path=None, destination_path=None,
               input_encoding='unicode', doctitle=True,
               initial_header_level=1):
    """
    Given an input string, returns a dictionary of HTML document parts.

    Dictionary keys are the names of parts, and values are Unicode strings;
    encoding is up to the client.

    Parameters:

    - `input_string`: A multi-line text string; required.
    - `source_path`: Path to the source file or object.  Optional, but useful
      for diagnostic output (system messages).
    - `destination_path`: Path to the file or object which will receive the
      output; optional.  Used for determining relative paths (stylesheets,
      source links, etc.).
    - `input_encoding`: The encoding of `input_string`.  If it is an encoded
      8-bit string, provide the correct encoding.  If it is a Unicode string,
      use "unicode", the default.
    - `doctitle`: Disable the promotion of a lone top-level section title to
      document title (and subsequent section title to document subtitle
      promotion); enabled by default.
    - `initial_header_level`: The initial level for header elements (e.g. 1
      for "<h1>").
    """
    overrides = {'input_encoding': input_encoding,
                 'doctitle_xform': doctitle,
                 'initial_header_level': initial_header_level}
    parts = core.publish_parts(
        source=input_string, source_path=source_path,
        destination_path=destination_path,
        writer_name='html', settings_overrides=overrides)
    return parts


def html_body(input_string, source_path=None, destination_path=None,               
              input_encoding='unicode', output_encoding='unicode',                 
              doctitle=True, initial_header_level=1):                              
    """                                                                            
    Given an input string, returns an HTML fragment as a string.                   
                                                                                   
    The return value is the contents of the <body> element.                        
                                                                                   
    Parameters (see `html_parts()` for the remainder):                             
                                                                                   
    - `output_encoding`: The desired encoding of the output.  If a Unicode         
      string is desired, use the default value of "unicode" .                      
    """                                                                            
    parts = html_parts(                                                            
        input_string=input_string, source_path=source_path,                        
        destination_path=destination_path,                                         
        input_encoding=input_encoding, doctitle=doctitle,                          
        initial_header_level=initial_header_level)                                 
    fragment = parts['html_body']                                                  
    if output_encoding != 'unicode':                                               
        fragment = fragment.encode(output_encoding)                                
    return fragment   

def safe_eval_val(v):
    if v.startswith("${") and v.endswith("}$"):
        v = v.strip("${}")
        return eval(v)
    return v

def build_post_form(params, method, url):
    fname = url.strip("/")
    form = '''
    <form name='{name}' action='{url}' method='{method}'>'''.format(name=fname,
                                                                 url=url,
                                                                 method=method)
    form += "<legend>%s API method</legend>" %(fname)
    form += '<fieldset>'
    for key, vals in params.items():
        hk = hash(key)
        form += '''
        <p>
        <label for="combo%s">%s</label>
        <select id="combo%s", name="%s" style="width: 200px;"
        onchange="$('input#text%s').val($(this).val());">''' %(hk,key,hk,key, hk)

        for v in vals:
            form += '''<option value={val}> {val} </option>\n'''.format(val=v)

        form += '''</select>
        <input id="text%s" style="margin-left: -203px; width: 180px;
height: 1.2em; border:0;" />''' %(hash(key))
        form += "</p>"
    form += '<input type="submit" value="Submit" class="button" />'
    form += '</fieldset>'
    form += '</form>'
    form += '\n\n'
    return form

def build_javascipt_poster(content, method, url):
    form  = '''
    <fieldset>
    <textarea id="{id}" rows=15 cols=30>                                                  
    {content}                                                                              
    </textarea>
<button onclick="rawPost('{url}', {id})">Submit</button>
    </fieldset>'''.format(url = url, content=content, id=abs(hash(url)))
    return form
                              
def decode_docstring(string, url, method):
    string  = unicode(string)
    html = html_body(string)
    regex = re.compile("<\!--.\s*?GET.*?-->",re.IGNORECASE|re.MULTILINE|re.DOTALL)
    get_params = regex.findall(html)
    forms = []
    for get_param in get_params :
        inputs = {}
        get_param = re.sub("^<\!--\s*?GET", "", get_param).strip()
        get_param  = get_param.replace("-->", "").strip()
        for line in get_param.split("\n"):
            name = line.split(":")[0]
            vals = "".join(line.split(":")[1:]).split(",")
            itms = []
            for v in vals:
                sev = safe_eval_val(v)
                if type(sev) == list:
                    itms.extend(sev)
                else:
                    itms.append(sev)
            inputs[name] = itms
        forms.append(build_post_form(inputs, method, url))

    return (html, forms)

