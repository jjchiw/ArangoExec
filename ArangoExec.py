import sublime, sublime_plugin, http.client, socket, types, threading, time, json

selectedIndexOptions = -1

class Options:
    def __init__(self, name):
        self.name     = name
        connections   = sublime.load_settings("ArangoExec.sublime-settings").get('connections')
        self.host     = connections[self.name]['host']
        self.port     = connections[self.name]['port']
        self.username = connections[self.name]['username']
        self.password = connections[self.name]['password']
        self.database = connections[self.name]['database']
        if 'service' in connections[self.name]:
            self.service  = connections[self.name]['service']

    def __str__(self):
        return self.name

    @staticmethod
    def list():
        names = []
        connections = sublime.load_settings("ArangoExec.sublime-settings").get('connections')
        for connection in connections:
            names.append(connection)
        names.sort()
        return names

class Command():

    FILE_TYPE_HTML = "html"
    FILE_TYPE_JSON = "json"
    FILE_TYPE_XML = "xml"
    MAX_BYTES_BUFFER_SIZE = 8192
    HTML_CHARSET_HEADER = "CHARSET"
    htmlCharset = "utf-8"

    def explain(self, query):
        requestObject = { 'query' : query }
        urlPart = "/_api/explain"

        self._execute(requestObject, urlPart)

    def execute(self, query):
        requestObject = { 'query' : query, 'count' : True, 'batchSize' :100 }
        urlPart = "/_api/cursor"
        self._execute(requestObject, urlPart) 

    def _execute(self, requestObject, urlPart):
        global selectedIndexOptions

        if selectedIndexOptions == -1 :
            selectedIndexOptions = 0

        names = Options.list()
        options = Options(names[selectedIndexOptions])

        host = options.host
        port = options.port
        timeoutValue = 500
        request_page = "/_db/"+ options.database + urlPart
        requestPOSTBody = json.dumps(requestObject)
        requestType = "POST"
        print(request_page)
        try:
            # if not(useProxy):
                #if httpProtocol == self.HTTP_URL:
            conn = http.client.HTTPConnection(host, port, timeout=timeoutValue)
                # else:
                #     if len(clientSSLCertificateFile) > 0 or len(clientSSLKeyFile) > 0:
                #         print "Using client SSL certificate: ", clientSSLCertificateFile
                #         print "Using client SSL key file: ", clientSSLKeyFile
                #         conn = httplib.HTTPSConnection(
                #             url, port, timeout=timeoutValue, cert_file=clientSSLCertificateFile, key_file=clientSSLKeyFile)
                #     else:
                #         conn = httplib.HTTPSConnection(url, port, timeout=timeoutValue)

            conn.request(requestType, request_page, requestPOSTBody)

            # else:
            #     print "Using proxy: ", proxyURL + ":" + str(proxyPort)
            #     conn = httplib.HTTPConnection(proxyURL, proxyPort, timeout=timeoutValue)
            #     conn.request(requestType, httpProtocol + url + request_page, requestPOSTBody)

            startReqTime = time.time()
            resp = conn.getresponse()
            endReqTime = time.time()

            startDownloadTime = time.time()
            (respHeaderText, respBodyText, fileType) = self.getParsedResponse(resp)
            endDownloadTime = time.time()

            latencyTimeMilisec = int((endReqTime - startReqTime) * 1000)
            downloadTimeMilisec = int((endDownloadTime - startDownloadTime) * 1000)

            respText = self.getResponseTextForPresentation(respHeaderText, respBodyText, latencyTimeMilisec, downloadTimeMilisec)

            panel = sublime.active_window().new_file()

            obj = json.loads(respBodyText)

            prettyRespBodyText = json.dumps(obj,
                                      indent = 2,
                                      ensure_ascii = False,
                                      sort_keys = False,
                                      separators = (',', ': '))

            panel.set_read_only(False)
            panel.set_syntax_file("Packages/JavaScript/JSON.tmLanguage")
            panel.run_command('append', {'characters': prettyRespBodyText})
            panel.set_read_only(True)

            conn.close()
        except (socket.error, http.client.HTTPException, socket.timeout) as e:
            print(e)
            # if not(isinstance(e, types.NoneType)):
            #     respText = "Error connecting: " + str(e)
            # else:
            #     respText = "Error connecting"
        except AttributeError as e:
            print(e)
            respText = "HTTPS not supported by your Python version"

    def getParsedResponse(self, resp):
        fileType = self.FILE_TYPE_HTML
        resp_status = "%d " % resp.status + resp.reason + "\n"
        respHeaderText = resp_status

        for header in resp.getheaders():
            respHeaderText += header[0] + ":" + header[1] + "\n"

            # get resp. file type (html, json and xml supported). fallback to html
            if header[0] == "content-type":
                fileType = self.getFileTypeFromContentType(header[1])

        respBodyText = ""
        self.contentLenght = int(resp.getheader("content-length", 0))

        # download a 8KB buffer at a time
        respBody = resp.read(self.MAX_BYTES_BUFFER_SIZE)
        numDownloaded = len(respBody)
        self.totalBytesDownloaded = numDownloaded
        while numDownloaded == self.MAX_BYTES_BUFFER_SIZE:
            data = resp.read(self.MAX_BYTES_BUFFER_SIZE)
            respBody += data
            numDownloaded = len(data)
            self.totalBytesDownloaded += numDownloaded

        respBodyText += respBody.decode(self.htmlCharset, "replace")

        return (respHeaderText, respBodyText, fileType)

    def getFileTypeFromContentType(self, contentType):
        fileType = self.FILE_TYPE_HTML
        contentType = contentType.lower()

        print ("File type: ", contentType)

        for cType in self.httpContentTypes:
            if cType in contentType:
                fileType = cType

        return fileType

    def getResponseTextForPresentation(self, respHeaderText, respBodyText, latencyTimeMilisec, downloadTimeMilisec):
        return respHeaderText + "\n" + "Latency: " + str(latencyTimeMilisec) + "ms" + "\n" + "Download time:" + str(downloadTimeMilisec) + "ms" + "\n\n\n" + respBodyText

def arangoChangeConnection(index):
    global selectedIndexOptions
    names = Options.list()
    selectedIndexOptions = index
    sublime.status_message(' SQLExec: switched to %s' % names[index])



class arangoListConnection(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.active_window().show_quick_panel(Options.list(), arangoChangeConnection)


class ArangoExplainCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        Options.list()
        for region in self.view.sel():
            # If no selection, use the entire file as the selection
            query = ''
            if region.empty() :
                query = self.view.substr(sublime.Region(0, self.view.size()))
            else:
                query = self.view.substr(sublime.Region(region.a, region.b))

            command = Command()
            command.explain(query)


class ArangoExecCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        Options.list()
        for region in self.view.sel():
            # If no selection, use the entire file as the selection
            query = ''
            if region.empty() :
                query = self.view.substr(sublime.Region(0, self.view.size()))
            else:
                query = self.view.substr(sublime.Region(region.a, region.b))

            command = Command()
            command.execute(query)
