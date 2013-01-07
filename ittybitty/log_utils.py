import logging
import json

from html_template import basepage

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'asctime' : '555',
            'module' : record.name,
            'level' : record.levelname,
            'message' : record.getMessage() }

        return json.dumps(log_record)

class JSONFileHandler(logging.FileHandler):
    def shutdown(self):
        '''
        Lets resturcture the log fiel so it looks a little nicer
        '''
        logs  = []
        with open(self.baseFilename, "r") as f:
            for line in f:
                logs.append(json.loads(line))
            print logs
        with open(self.baseFilename, "w") as f:
            f.write(json.dumps(logs))


LOG_PAGE_STYLE = '''
tr.WARNING {
background-color:yellow;
}
tr.ERROR {
background-color:orange;
}
tr.CRITICAL {
background-color:red;
}
tr.DEBUG {
font-color:grey;
}
'''

class HtmlLogPage(basepage):
    def __init__(self, *args, **kwargs):
        '''
        Represents the HTML log page. This opject will build the html log page
        from the json logs stored in :param:`logfile`. :param`:`url` is the
        the url of this page. (This is the url that the form will sent its GET
        request to.
        '''
        basepage.__init__(self, *args, **kwargs)
        self.json_logs = []
        self.json_log_file = None
        self._params = {}
        self.styles.append(LOG_PAGE_STYLE)


    @property
    def filter_params(self):
        return self._params

    @filter_params.setter
    def filter_params(self, params):

        '''
        This will build the html page. :parm:`params` speciefies if we want to
        filter out of the core json file. So only json log records wich have a
        subset of the same key, value pairs as params will be inclided in the html
        page
        '''
        logs  = []
        with open(self.json_log_file, "r") as f:
            for line in f:
                logs.append(json.loads(line))

        self.json_logs = logs 

        matched_list = []
        for log in self.json_logs:
            if params :
                if set(params.items()).issubset(set(log.items())):
                    matched_list.append(log)
            else:
                matched_list.append(log)
        

        table = '''<table>
                    <tr>
                        <th> Time </th>
                        <th> Module </th>
                        <th> Level </th>
                        <th> Message </th>
                    </tr>'''
        

        for item in matched_list :
            table+= '''<tr class="{level}">
                        <td>{time}</td>
                        <td>{module}</td>
                        <td>{level}</td>
                        <td>{message}</td></tr>'''.format(time=item["asctime"],
                                                         module=item["module"],
                                                         level=item["level"],
                                                         message=item["message"])
        table += '</table>'

        
        self.body += '<h1> Log Viewer </h1>\n'
        self.body += '<p> These same logs can be found in JSON format on <a\
                            href="json-logs">here</a> </p>'
        self.body += self.build_filter_box()
        self.body += table

        print self.body

    def build_filter_box(self):
        '''
        This bilds a little filter box for the top of the page
        '''
        form = '''
        <form name="filter" action={url} method="get">
        <h3>Select what you want to filter by</h3>
        <label> LogLevel </label>
        <select name="level">
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="ERROR">ERROR</option>
        </select>

        <label>Logger</label>
        <select name="module">
            {module_options}
        </select>
        <input type="submit" value="Filter">
        <a href="{url}">Reset Filtering</a>
        </form></hr>\n\n'''.format(module_options = self._get_module_opts(), url=self.url)

        return form

    def _get_module_opts(self):
        modules = []
        for record in self.json_logs:
            modules.append(record["module"])
        modules = set(modules)

        opts = ''
        for module in modules:
            opts += '<option value="{m}">{m}</option>\n'.format(m=module)
        return opts





        
