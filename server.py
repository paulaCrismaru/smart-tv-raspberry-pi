""""
This server will run on the raspberry pi and will receive
commands from the andoid device
"""

import datetime
import SimpleHTTPServer
import SocketServer
import json
import sys
import threading
import time
import urllib2

from app_navigators import exceptions
from selenium.common import exceptions as selenium_exceptions
from browsers.firefox import FireFox
from config import config
from etc.response import Response
import browsers


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""
        global FIRST_REQUEST
        path = urllib2.unquote(self.path)
        print path, "dupa unquote"
        command = path.split('/')
        command.remove('')
        args = {
            "code": 200,
            "buttons_list": None,
            "fields_list": None,
            "current_page": None,
            "resources_list": None
        }
        args["message"] = "OK"
        response_args = {}
        try:
            if FIRST_REQUEST:
                FIRST_REQUEST = False
            elif path in ["/get-current-options", "/insert-in-search",
                        "/scroll-down", "/scroll-up"]:
                response_args = BROWSER.get_current_page_options()
            else:
                response_args = BROWSER.handle_get(path)
                # BROWSER.navigate_to(path)
        except Exception as ex:
            args["code"] = 404
            args["message"] = str(ex)
        finally:
            print response_args
            if response_args is not None:
                args.update(response_args)
            args['current_page'] = BROWSER.current_url
            response = Response(**args)
            print args
            self.send_response(response)

    def do_POST(self):
        HAS_CLIENTS = True
        path = urllib2.unquote(self.path)
        current_page = BROWSER.current_url.encode('utf-8')
        data = None
        args = {
            "code": 200,
            "buttons_list": None,
            "fields_list": None,
            "current_page": BROWSER.current_url.encode('utf-8'),
            "resources_list": None
        }
        try:
            data = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(data)
        except ValueError:
            pass
        try:
            if path == "back":
                response_args = BROWSER.do_back()
            elif path == "/scroll-up":
                BROWSER.scroll_up()
            elif path == "/scroll-down":
                BROWSER.scroll_down()
            else:
                response_args = BROWSER.handle_post(path, data)
                args.update(response_args)
                # response = Response(code=code, current_page=current_page,
                #                     buttons=buttons_list, fields=fields_list)
        except selenium_exceptions.NoSuchElementException or IndexError:
            args['code'] = 405
            args['message'] = "Not allowed"
            # response = Response(code=405, message="Not allowed",
            #                     current_page=current_page,
            #                     buttons=buttons_list, fields=fields_list)
        # except Exception:
        #     response = Response(code=405, message="Not allowed",
        #                         current_page=current_page,
        #                         buttons=buttons_list, fields=fields_list)
        finally:
            response = Response(**args)
            print args
            self.send_response(response)

    def send_response(self, response):
        buttons_list = response.buttons
        fields_list = response.fields
        resources_list = response.resources_list
        response_args = {}
        print BROWSER.current_url
        if BROWSER.current_url == 'about:blank':
            pass
        elif buttons_list is None and fields_list is None:
            try:
                response_args = BROWSER.get_current_page_options()
                buttons_list = response_args['buttons_list']
                fields_list = response_args['fields_list']
                resources_list = response_args['resources_list']
                # buttons_list, fields_list, resources_list = BROWSER.get_current_page_options()
            except exceptions.AppHandlerException:
                pass
        elif buttons_list is None:
            response_args = BROWSER.get_current_page_options()
            buttons_list = response_args['buttons_list']
            resources_list = response_args['resources_list']
        elif fields_list is None:
            response_args = BROWSER.get_current_page_options()
            # buttons_list = response_args['buttons_list']
            fields_list = response_args['fields_list']
            # resources_list = response_args['resources_list']
        SimpleHTTPServer.SimpleHTTPRequestHandler.send_response(self, response.code, response.message)
        # self.send_header("Content-Type", 'text/html; charset=utf-8')
        self.send_header("Content-Type", 'application/json; charset=utf-8')
        # x = BROWSER.current_url.split("//")
        # self.send_header("current_page", x[1].split("/")[0].encode('utf-8'))
        # self.send_header("current_page", BROWSER.current_url.replace(APP_URL, "").encode('utf-8'))
        self.send_header("current_page", BROWSER.current_url.encode('utf-8'))
        self.send_header("Content-Length", 0)
        # for item in ["buttons_list", "fields_list", "resources_list"]:
        #     if item is not None:
        #         self.send_header(item.replace("_list", ''), ','.join(eval(item)))
        #     else:
        #         self.send_header(item.replace("_list", ''), '')
        if buttons_list is not None:
            self.send_header("buttons_list", ','.join(buttons_list))
        else:
            self.send_header("buttons_list", '')
        if fields_list is not None:
            self.send_header("input_fields", ','.join(fields_list))
        else:
            self.send_header("input_fields", '')
        if resources_list is not None:
            self.send_header("resources_list", ','.join(resources_list))
        else:
            self.send_header("resources_list", '')
        for variable in response.__dict__:
            if variable not in \
                    ["input_fields", "buttons", "current_page", "code", "resources_list"]:
                value = getattr(response, variable)
                if value is None:
                    self.send_header(variable, '')
                else:
                    self.send_header(variable, value)
        self.end_headers()


class Server(SocketServer.TCPServer):
    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, host, port):
        self.url = "http://%s:%s" % (host, port)
        self.log_message("Server started at %s" % (self.url))
        SocketServer.TCPServer.__init__(self, (host, port), Handler)

    def log_message(self, format, *args):
        sys.stderr.write("[%s] %s\n" %
                         (self.log_date_time_string(),
                          format % args))

    def log_date_time_string(self):
        """Return the current time formatted for logging."""
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
            day, self.monthname[month], year, hh, mm, ss)
        return s


def wait_for_clients():
    while True:
        has_clients_ = HAS_CLIENTS
        now = datetime.datetime.now()
        if (now.minute - TIME_START.minute) >= TIME_TO_WAIT:
            server.shutdown()
            BROWSER.quit()
            return
        time.sleep(1)
        if has_clients_:
            return



BROWSER = None
APP_URL = None
TIME_START = None
TIME_TO_WAIT = None
HAS_CLIENTS = False
FIRST_REQUEST = True
if __name__ == "__main__":
    arguments = config.parse_arguments()
    parsed_arguments = arguments.parse_args(sys.argv[1:])

    # APP_CONF = config.compute_config(parsed_arguments.config, "app_server")
    # APP_PROTOCOL, APP_HOST, APP_PORT = APP_CONF.protocol, APP_CONF.host, APP_CONF.port
    # APP_URL = APP_CONF.protocol + "://" + APP_HOST + ":" + APP_PORT + "/"

    ANDROID_CONF = config.compute_config(parsed_arguments.config, "android_server")
    ANDROID_HOST, ANDROID_PORT = ANDROID_CONF.host, ANDROID_CONF.port
    # BROWSER = FireFox(config.compute_config(parsed_arguments.config, "browser"))
    # BROWSER = FireFox(None)
    TIME_TO_WAIT = int(ANDROID_CONF.time_to_wait)


    BROWSER_CONF = config.compute_config(parsed_arguments.config, "browser")

    module = __import__("browsers." + BROWSER_CONF.browser_module,  fromlist = ["*"])
    browser_class = getattr(module, BROWSER_CONF.browser_class_name)
    BROWSER = browser_class(None)

    server = Server(ANDROID_HOST, int(ANDROID_PORT))
    TIME_START = datetime.datetime.now()
    thread = threading.Thread(target=wait_for_clients)
    thread.start()
    server.serve_forever()

