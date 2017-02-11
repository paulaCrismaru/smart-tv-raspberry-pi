import abc


class BaseNavigator(object):

    name = None
    app_url = None

    def __init__(self, browser, conf=None):
        self.browser = browser

    @abc.abstractmethod
    def handle_get(self, path):
        pass

    @abc.abstractmethod
    def handle_post(self, path, data=None):
        pass

    @abc.abstractmethod
    def get_current_page_options(self):
        pass

    @classmethod
    @abc.abstractmethod
    def get_provider(cls, name):
        pass

    @abc.abstractmethod
    def is_current_provider(self):
        pass


