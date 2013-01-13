from version import ITTYBITTY_VERSION
DEFAULT_STYLE = '''

.input {
    border: 1px solid #006;
    background: #ffc;
    margin-left: 4.5em;
}
.button {
    border: 1px solid #006;
    background: #9cf;
}
label {
    display: block;
    width: 4em;
    float: left;
    text-align: right;
    margin-right: 0.5em;
}
br { clear: left; }

fieldset
{
border: 1px solid #781351;
width: 20em
}

legend
{
color: #006;;
background: #ffa20c;
border: 1px solid #006;
padding: 2px 6px
}


h1 {
font-family:"Trebuchet MS", Arial, Helvetica, sans-serif; 
font-size:1em
text-decoration:underline
}

table
{
font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
width:100%;
border-collapse:collapse;
}



td{
text-align:center;
font-size:1em;
border:1px solid #006699;
padding:3px 7px 2px 7px;
}

th {
background-color:#6699CC;
border:1px solid #006699;
}
'''
import time

class html_config(object):
    def __init__(self, host, port, start_time):
        self.host = host
        self.port = port
        self.start_time = start_time
        self.header_items = {}

    @property
    def page_header(self):
        base_dict =  {'ittybitty' : ITTYBITTY_VERSION,
                    'Service Uptime' : self.uptime,
                    'Host' : self.host,
                    'Port' : self.port}
        base_dict.update(self.header_items)
        return base_dict 

    @property
    def uptime(self):
        return time.time() - self.start_time
                        


class basepage(object):
    def __init__(self, url, html_config):
        self.url = url
        self.html_config = html_config 
        self.styles = []
        self.styles.append(DEFAULT_STYLE)

        self.body = ''
        self.header = ''
 
    @property
    def page_header(self):
        tbl =  '''
        <table id="page_header">
        <tr>'''
        print self.html_config.page_header
        for k, v in self.html_config.page_header.items() :
            tbl += '<th>{k} : {v}</th>\n'.format(k=k, v=v)


        tbl += '</tr></table>'
        return tbl

    @property
    def html(self):
        return '''
        <html>
        <HEAD>
        {head}
        <style>
        {styles}
        </style>
        </HEAD>
        <BODY>
        {body}
        </BODY></HTML>'''.format(styles = "\n".join(self.styles),
                                 head = self.header,
                                 body = self.page_header + self.body)

def dict_to_html_table(nested_list, header=False):
    '''
    This function takes in a nested list and returns a html table.
    If :param:`header` is true then te first nested list is thought
    to be a list of headers.
    '''
    tbl = '<table>'
    if header:
        hd = nested_list[0]
        tbl += "<tr>\n"
        for i in hd :
            tbl += "<th>%s</th>" %str(i)
        tbl += "</tr>"
    
        nested_list = nested_list[1:]
    for l in nested_list:
        tbl += "<tr>"
        for i in l :
            tbl += "<td>%s</td>" %str(i)
        tbl += "</tr>"
    tbl += "</table>"
    return tbl




