import abc


class BaseBrowser(object):
    @abc.abstractmethod
    def add_provider(self, provider):
        pass

    @abc.abstractmethod
    def navigate_to(self, url):
        pass

    @classmethod
    @abc.abstractmethod
    def get_provider(cls, name):
        pass

    @abc.abstractmethod
    def get_current_page_options(self):
        pass

    @abc.abstractmethod
    def scroll_down(self):
        pass

    @abc.abstractmethod
    def scroll_up(self):
        pass

    @abc.abstractmethod
    def handle_get(self, url):
        pass

    @abc.abstractmethod
    def handle_post(self, url, data=None):
        pass