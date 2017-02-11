import abc


class BaseNavigator:
    connect_url = "/connect"
    send_credentials = "/send-credentials"
    click_login = "/click-login"
    accept_authorization_url = "/accept-authorization"
    deny_authorization_url = "/deny-authorization"
    input_field_text = "/input-search"
    click_search = "/click-search"
    login_app_button = "button"

    def get_class_variables(self):
        return [item for item in dir(self)
                if not item.startswith('__') and
                item not in self.__dict__ and
                not callable(getattr(self, item))]

    @abc.abstractmethod
    def next(self):
        pass

    @abc.abstractmethod
    def prev(self):
        pass

    @abc.abstractmethod
    def pause(self):
        pass

    @abc.abstractmethod
    def play(self):
        pass

