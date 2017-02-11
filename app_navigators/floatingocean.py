import collections
import copy
import json
import requests
import time
import urllib

from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.by import By

from cloud_services_providers.base import BaseNavigator
from cloud_services_providers.dropbox import DropboxNavigator
from cloud_services_providers.gdrive import GdriveNavigator


class FloatingOcean():

    name = "FloatingOcean"
#    app_url = "http://localhost:5000"
    app_url = "http://192.168.1.168:5000"
    providers_list = {}
    gallery_options = ['start', 'next', 'prev', 'close']
    resources_list = ['/start', '/next', '/prev', '/close']
    resources = []

    def __init__(self, browser, conf=None):
        # BaseNavigator.__init__(self, browser, conf)
        self.browser = browser
        FloatingOcean.providers_list[DropboxNavigator.name] = DropboxNavigator(self.browser, conf)
        FloatingOcean.providers_list[GdriveNavigator.name] = GdriveNavigator(self.browser, conf)

    def click_button(self, form_id, button_name):
        try:
            form = self.browser.find_element_by_id(form_id)
            button = form.find_element_by_name(button_name)
            button.click()
        except:
            raise

    def click_login_button_app(self, service):
        try:
            elements = self.browser.find_element_by_id("button-" + service.title())
            elements.click()
        except:
            raise

    def start(self):
        element = self.browser.find_elements_by_id("1")
        element[0].click()
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": None
        }
        response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('start')
        response["resources_list"] = copy.deepcopy(self.resources_list).remove('/start')
        return response

    def next(self):
        element = self.browser.find_elements_by_class_name("right")
        element[0].click()
        # return copy.deepcopy(self.gallery_options).remove('next')
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": None
        }
        response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('next')
        response["resources_list"] = copy.deepcopy(self.resources_list).remove('/next')
        return response

    def prev(self):
        element = self.browser.find_elements_by_class_name("left")
        element[0].click()
        # return copy.deepcopy(self.gallery_options).remove('prev')
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": None
        }
        response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('prev')
        response["resources_list"] = copy.deepcopy(self.resources_list).remove('/prev')
        return response

    def close(self):
        element = self.browser.find_elements_by_class_name("close")
        element[0].click()
        # return copy.deepcopy(self.gallery_options).remove('close')
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": None
        }
        response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('close')
        response["resources_list"] = copy.deepcopy(self.resources_list).remove('/close')
        return response

    # def get_home_buttons(self):
    #     # elements = self.find_elements_by_tag_name("input")
    #     # toggle_object = self.browser.find_element(By.XPATH, toogle)
    #     # return [item.get_attribute("value").encode('utf-8') for item in elements]
    #     # // *[ @ id = "button-Dropbox"]
    #     # /html/body/div[1]/div/div[2]/div[2]/div[2]
    #     pass

    def click_expand_collapse(self, path):
        path = urllib.unquote(path)
        path = path.replace(" ", "-")
        folders = path.split("/")
        folders.remove("")
        pattern_xpath = '//*[@id=\"-{}\"]/../a'
        last_toogle = True
        for folder in folders:
            if folders.index(folder) < (len(folders) - 1):
                toogle = pattern_xpath.format('-'.join(folders[:folders.index(folder) + 1]))
                toggle_object = self.browser.find_element(By.XPATH, toogle)
                is_expanded = False
                try:
                    toggle_parent = self.browser.find_element(By.XPATH, toogle + "/../ul")
                    is_expanded = toggle_parent.get_attribute("aria-expanded")
                except:
                    pass
                toggle_object.click()
                time.sleep(0.5)

    def get_home_buttons(self):
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": []
        }
        parent_element_xpath = "/html/body/div[1]/div/div[2]/div[2]"
        parent_element = self.browser.find_element(By.XPATH, parent_element_xpath)
        buttons = parent_element.find_elements_by_xpath('//*[contains(@id, "button-")]')
        response["buttons_list"] = [button.text.encode('utf-8') for button in buttons]
        for button in response["buttons_list"]:
            service = button.replace("Connect ", "")
            response["resources_list"] += ["/connect-{}".format(service.lower())]
        return response
        # return [button.text.encode('utf-8') for button in buttons]

    def home(self):
        self.browser.get(self.app_url)
        return self.get_home_buttons()

    def handle_get(self, path):
        args = {
            "code": 200,
            "buttons_list": None,
            "resources_list": None,
            "fields_list": None,
            "menu": None
        }
        if path.endswith("/"):
            path = path[:-1]
        response_args = {}
        if path.startswith('expand/'):
            self.click_expand_collapse(path[len('expand'):])
            response_args = self.get_current_page_options()
            # args["buttons_list"] = self.get_current_page_options()
        elif FloatingOcean.app_url.startswith(path):
            response_args = self.home()
            print response_args
            # args["buttons_list"] = self.home()
        elif path == "menu":
            response = requests.get(FloatingOcean.app_url + "/menu")
            # args["menu"] = json.loads(response.content, encoding='utf-8')
            args["menu"] = self.convert(json.loads(response.content))
        else:
            print "GET", "/" + path
            self.browser.get(FloatingOcean.app_url + "/" + path)
            # args["buttons_list"], args["fields_list"] = self.get_current_page_options()
        if response_args is not None:
            args.update(response_args)
        return args

    def handle_post(self, path, data=None):
        args = {
            "code": 200,
            "buttons_list": None,
            "fields_list": None,
            "menu": None,
            "resources_list": None
        }
        response_args = {}
        if path.endswith("/"):
            path = path[:-1]
        print path
        try:
            if not self.path_is_valid(path): # OK
                print "not valid path"
                # args["buttons_list"], args["fields_list"], args["resources_list"] = \
                #     self.get_current_page_options()
                response_args = self.get_current_page_options()
                args["code"] = 404
            elif path == "/start":
                print "intra in start"
                # args["buttons_list"]= self.start()
                response_args = self.start()
            elif path == "/next":
                response_args = self.next()
                # args["buttons_list"] = self.next()
            elif path == "/prev":
                response_args = self.prev()
                # args["buttons_list"] = self.prev()
            elif path == "/close":
                response_args = self.close()
                # args["buttons_list"] = self.close()
            elif path.startswith(BaseNavigator.send_credentials): # OK
                _, service_name = path.split(BaseNavigator.send_credentials + "-")
                provider = self.get_provider(service_name)
                try:
                    email = data[u'email']
                except KeyError:
                    email = None
                try:
                    password = data[u'password']
                except KeyError:
                    password = None
                response_args = provider.do_login_service(email, password)
                # args["buttons_list"] = provider.do_login_service(email, password)
            elif path.startswith(BaseNavigator.click_login): # OK
                _, service_name = path.split(BaseNavigator.click_login + "-")
                provider = self.get_provider(service_name)
                # args["buttons_list"], args["resources_list"], args["resources_list"] = provider.click_login_service()
                response_args = provider.click_login_service()
            elif path.startswith(BaseNavigator.accept_authorization_url):
                _, service_name = path.split(BaseNavigator.accept_authorization_url + "-")
                provider = self.get_provider(service_name)
                provider.accept_authorization()
                # args["buttons_list"], args["fields_list"], args["resources_list"] = self.get_current_page_options()
                response_args = self.get_current_page_options()
            elif path.startswith(BaseNavigator.deny_authorization_url):
                _, service_name = path.split(BaseNavigator.deny_authorization_url + "-")
                provider = self.get_provider(service_name)
                provider.deny_authorization()
                # args["buttons_list"], args["fields_list"], args["resources_list"] = self.get_current_page_options()
                response_args = self.get_current_page_options()
            elif path.startswith(BaseNavigator.connect_url): # OK
                _, service_name = path.split(BaseNavigator.connect_url + "-")
                provider = self.get_provider(service_name)
                self.click_login_button_app(service_name)
                # args["buttons_list"], args["fields_list"], args["resources_list"] = provider.is_redirect()
                response_args = provider.is_redirect()
        except IndexError:
            args["code"] = 405
        except selenium_exceptions.NoSuchElementException:
            args["code"] = 405
        args.update(response_args)
        return args
        # return code, buttons_list, fields_list

    def path_is_valid(self, path):
        base = BaseNavigator()
        if path == '':
            return True
        for item in base.get_class_variables():
            try:
                resource, service = path.split(getattr(base, item) + '-')
            except ValueError:
                continue
            if resource != '':
                continue
            if service in self.providers_list.keys():
                return True
        if path in ["/start", "/close", "/next", "/prev"]:
            return True

        return False

    def get_current_page_options(self):
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": None
        }
        fields = None
        buttons = None
        resources = None
        path = self.browser.current_url.replace(FloatingOcean.app_url, "")
        if path == '/':
            # buttons = self.get_home_buttons()
            response = self.get_home_buttons()
        elif self.browser.current_url.encode('utf-8').startswith('https://accounts.google.com/o/oauth2/auth'):
            response["buttons_list"] = ["Allow Gdrive", "Deny Gdrive"]
            response["resources_list"] = ["/accept-authorization-gdrive", "/deny-authorization-gdrive"]
        # elif path.startswith(BaseNavigator.send_credentials):
        #     return
        # elif path.startswith(BaseNavigator.click_login):
        #     return
        # elif path.startswith(BaseNavigator.accept_authorization_url):
        #     []
        # elif path.startswith(BaseNavigator.deny_authorization_url):
        #     return
        # elif path.startswith(BaseNavigator.service_auth_url):
        else:
            for provider_name in FloatingOcean.providers_list:
                provider = FloatingOcean.providers_list.get(provider_name)
                if path.startswith(provider.service_auth_url):
                    response = provider.is_redirect()
                    # buttons, fields = provider.is_redirect()
                    break
                else:
                    # buttons = ["start", "next", "prev", "close"]
                    response["buttons_list"] = ["start", "next", "prev", "close"]
                    response["resources_list"] = ["/start", "/next", "/prev", "/close"]
                    # resources = ["/start", "/next", "/prev", "/close"]
        return response

    @classmethod
    def get_provider(cls, name):
        return cls.providers_list.get(name)

    def convert(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert, data))
        else:
            return data

    def is_current_provider(self, url):
        if url.startswith(FloatingOcean.app_url):
            return True
        for provider_name in FloatingOcean.providers_list:
            provider = FloatingOcean.get_provider(provider_name)
            if url.startswith(provider.service_auth_url):
                return True
        if self.browser.current_url.encode('utf-8').startswith("https://accounts.google.com/o/oauth2/auth?"):
            return True
        return False

    @classmethod
    def supports(cls, url):
        avaliable_urls = [
            FloatingOcean.app_url, "/start", "/next", "/prev", "/close", "/expand/", "/menu"
        ]
        for provider_name in cls.providers_list:
            avaliable_urls += cls.get_provider(provider_name).get_supported_resources()
        return url in avaliable_urls
