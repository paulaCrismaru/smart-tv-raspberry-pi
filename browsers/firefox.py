import abc
from app_navigators import exceptions
from app_navigators.floatingocean import FloatingOcean
from app_navigators.youtube import YoutubeNavigator
from selenium.webdriver.firefox.webdriver import WebDriver
import base


class FireFox(base.BaseBrowser, WebDriver):
    supported_app_list = {}

    def __init__(self, conf):
        WebDriver.__init__(self)
        self.maximize_window()
        self.poz = 0
        self.conf = conf
        self.add_provider(FloatingOcean)
        self.add_provider(YoutubeNavigator)
        # self.get(FloatingOcean.app_url)

    def add_provider(self, provider):
        FireFox.supported_app_list[provider.name] = provider(browser=self, conf=self.conf)

    def navigate_to(self, url):
        # provider = FireFox.get_provider(FireFox.current_provider_name)
        # self.get(provider.app_url[:-1] + url)
        self.get(url)

    @classmethod
    def get_provider(cls, name):
        return cls.supported_app_list.get(name)

    def get_current_page_options(self):
        for app_name in FireFox.supported_app_list:
            app = FireFox.supported_app_list.get(app_name)
            if app.is_current_provider(self.current_url):
                break
            else:
                app = None
        if app is not None:
            return app.get_current_page_options()
        else:
            raise exceptions.AppHandlerException("App not supported!")

    def scroll_down(self):
        self.poz += 500
        self.execute_script("window.scrollTo(0, {});".format(self.poz))

    def scroll_up(self):
        self.poz -= 500
        self.execute_script("window.scrollTo(0, {});".format(self.poz))

    def handle_get(self, url):
        args = {
            "buttons_list": None,
            "fields_list": None,
        }
        for app_name in FireFox.supported_app_list:
            app = FireFox.supported_app_list.get(app_name)
            if url[1:].startswith(app.app_url):  #
                return app.handle_get(url[1:])  #
        for app_name in FireFox.supported_app_list:
            app = FireFox.supported_app_list.get(app_name)
            if app.is_current_provider(self.current_url):
                # print app_name, "is current provider"
            # if app.is_current_provider(url[1:]):
                # print app_name, "e current provider"
                result = app.handle_get(url[1:])
                return result
        else:
            print "arunca exceptie"
            raise exceptions.AppHandlerException("App not supported!")

    def handle_post(self, url, data=None):
        # for provider in FireFox.supported_app_list:
        #     if url.starts_with(provider.app_url):
        #         FireFox.current_provider_name = provider.name
        # provider = FireFox.get_provider(FireFox.current_provider_name)
        # for provider in FireFox.supported_app_list:
        #     p = FireFox.get_provider(provider)
        #     print p
        # if url.startswith(provider.url):
        for app_name in FireFox.supported_app_list:
            app = FireFox.supported_app_list.get(app_name)
            if app.is_current_provider(self.current_url):
            # if app.is_current_provider(url[1:]):
                # print app_name, "e current provider"
                result = app.handle_post(url, data)
                print "in firefox handle-post"
                print app_name
                print result
                return result
        else:
            print "arunca exceptie"
            raise exceptions.AppHandlerException("App not supported!")

    @classmethod
    def get_current_provider(cls):
        return cls.get_provider(cls.current_provider_name)
        # for provider_name in FireFox.supported_app_list:
        #     provider = cls.get_provider(provider_name)
        #     if provider.is_current_provider(url):
        #         cls.current_provider_name = provider_name

    def do_back(self):
        self.browser.execute_script("window.history.go(-1)")
