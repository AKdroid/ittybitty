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

LOG_COLORS = {  'INFO'  :   'black',
                'DEBUG' :   'grey',
                'WARNING':  'pink',
                'ERROR' : 'orange',
                'CRITICAL':'red' } 

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


class HtmlLogTail(basepage):
    def __init__(self, *args, **kwargs):
        '''
        A log tail utlity based on Ajax
        '''
        basepage.__init__(self, *args, **kwargs)

        self.header += r'''
<script>
function createRequest() {
 var request = null;
  try {
   request = new XMLHttpRequest();
  } catch (trymicrosoft) {
   try {
     request = new ActiveXObject("Msxml2.XMLHTTP");
   } catch (othermicrosoft) {
     try {
      request = new ActiveXObject("Microsoft.XMLHTTP");
     } catch (failed) {
       request = null;
     }
   }
 }

 if (request == null) {
   //alert("Error creating request object!");
 } else {
   return request;
 }
}

var request1 = createRequest();
var request2 = createRequest();
var request2A = createRequest();
var request3 = createRequest();

function getLog(timer) {

var url = "/html-logs";
request1.open("GET", url, true);
request1.onreadystatechange = updatePage;
request1.send(null);
startTail(timer);
}

function startTail(timer) {
if (timer == "stop") {
stopTail();
} else {
t= setTimeout("getLog()",1000);
}
}

function stopTail() {
clearTimeout(t);
var pause = "The log viewer has been paused. To begin viewing again, click the Start Viewer button.";
logDiv = document.getElementById("log");
var newNode=document.createTextNode(pause);
logDiv.replaceChild(newNode,logDiv.childNodes[0]);
}

function updatePage() {
if (request1.readyState == 4) {
if (request1.status == 200) {
var currentLogValue = request1.responseText.split("\n");
eval(currentLogValue);
logDiv = document.getElementById("log");
var logLine = ' ';
for (i=0; i < currentLogValue.length - 1; i++) {
logLine += currentLogValue[i] + "<br/>\n";
}
logDiv.innerHTML=logLine;
}
}}
</script>
        '''
        self.body += '''

<div id="message" style="border:solid 1px #dddddd; width:500px;
margin-left:25px; font-size:14px; font-family:san-serif,tahoma,arial;
padding-left:15px; padding-right:15px; padding-top:10px; padding-bottom:20px;
margin-top:20px; margin-bottom:10px; text-align:left;">
<p>
<h2>Log Viewer</h2>

<div>
<button onclick="getLog('start');">Start Viewer</button>
<button onclick="stopTail();">Stop Viewer</button>
</div>
explanation.  This is a working example of the AJAX Log File Viewer
discussed there.
</p>
</div>
</br
</hr>
<div id="log" style="border:solid 1px #dddddd; margin-left:25px;
margin-top:20px; font-size:11px;
padding-left:15px; padding-right:15px; padding-top:100px; padding-bottom:20px;
margin-bottom:10px; text-align:left; height: 150px; overflow:auto;">
<h3>Log Viewer Div</h3>
This is the Log Viewer. To begin viewing the log live in this window, click
Start Viewer. To stop the window refreshes, click Stop Viewer.
</div>

    '''

        
