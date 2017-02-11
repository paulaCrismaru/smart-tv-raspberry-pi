import copy
import time

from selenium.webdriver.common.by import By

from cloud_services_providers.base import BaseNavigator


class DropboxNavigator():
    name = "dropbox"

    service_auth_url = "https://www.dropbox.com/1/oauth2/authorize?"
    service_auth_cookie = "cookie_notif"
    service_login_form_css_selector = ".clearfix.credentials-form.login-form"
    service_email_field_name = "login_email"
    service_email_field_css_selector = ".text-input-input.autofocus"
    service_password_field_name = "login_password"
    service_password_field_css_selector = ".password-input.text-input-input"
    service_login_button_css_selector = ".login-button.button-primary"
    service_authorize_form_id = "regular-login-forms"
    service_allow_button_name = "allow_access"
    service_deny_button_name = "deny_access"
    service_authorize_box_id = "auth"

    def __init__(self, browser, conf=None):
        self.browser = browser
        base = BaseNavigator()
        for variable_name in base.get_class_variables():
            if variable_name == "login_app_button":
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name.title())
            else:
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name)
            setattr(DropboxNavigator, variable_name, variable_value)


    def do_login_service(self, email, password):
        response = {
            "buttons_list": ['sign-in'],
            "resources_list": ['/click-login-dropbox']
        }
        self.insert_in_login_field(
            self.service_authorize_form_id,
            self.service_email_field_css_selector,
            self.service_email_field_name, email)
        self.insert_in_login_field(
            self.service_authorize_form_id,
            self.service_password_field_css_selector,
            self.service_password_field_name, password)
        return response

    def insert_in_login_field(self, form_id, field_css_selector, field_name, data):
        form = self.browser.find_element_by_id(form_id)
        elements = form.find_elements_by_css_selector(field_css_selector)
        for element in elements:
            if element.get_attribute("name") == field_name:
                element.clear()
                element.send_keys(data)
                return

    def click_login_service(self):
        response = {
            "buttons_list": ["allow", "deny"],
            "resources_list": [
                "/accept-authorization-dropbox",
                "/deny-authorization-dropbox"]
        }
        form = self.browser.find_element_by_css_selector(self.service_login_form_css_selector)
        button = form.find_element_by_css_selector(self.service_login_button_css_selector)
        button.click()
        return response

    def accept_authorization(self):
        try:
            self.click_button(self.service_authorize_box_id, self.service_allow_button_name)
        except:
            raise

    def deny_authorization(self):
        try:
            self.click_button(
                self.service_authorize_box_id,
                self.service_deny_button_name)
            time.sleep(0.5)
        except:
            raise

    def click_button(self, form_id, button_name):
        try:
            form = self.browser.find_element_by_id(form_id)
            button = form.find_element_by_name(button_name)
            button.click()
        except:
            raise

    def is_redirect(self):
        response = {
            "buttons_list": None,
            "fields_list": None,
            "resources_list": None
        }
        time.sleep(2)
        if self.browser.current_url.encode('utf-8').startswith(self.service_auth_url):
            if self.browser.get_cookie(self.service_auth_cookie) is not None\
                    or self.browser.get_cookie("bjar") is not None:
            # if self.browser.current_url.contains("auth-finish"):
                response["buttons_list"] = ['Allow Dropbox', 'Deny Dropbox']
                response["resources_list"] = [
                    '/accept-authorization-dropbox',
                    '/deny-authorization-dropbox'
                ]
            else:
                response["buttons_list"] = ["sign-in"]
                response["fields_list"] = ['email', 'password']
                response["resources_list"] = ["/click-login-dropbox"]
                # return ['sign-in'], ['email', 'password'], None
        return response

    # def start(self):
    #     element = self.browser.find_elements_by_id("1")
    #     element[0].click()
    #     response = {
    #         "buttons_list": None,
    #         "fields_list": None,
    #         "resources_list": None
    #     }
    #     response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('start')
    #     response["resources_list"] = copy.deepcopy(self.resources_list).remove('/start')
    #     return response
    #
    # def next(self):
    #     element = self.browser.find_elements_by_class_name("right")
    #     element[0].click()
    #     # return copy.deepcopy(self.gallery_options).remove('next')
    #     response = {
    #         "buttons_list": None,
    #         "fields_list": None,
    #         "resources_list": None
    #     }
    #     response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('next')
    #     response["resources_list"] = copy.deepcopy(self.resources_list).remove('/next')
    #     return response
    #
    # def prev(self):
    #     element = self.browser.find_elements_by_class_name("left")
    #     element[0].click()
    #     # return copy.deepcopy(self.gallery_options).remove('prev')
    #     response = {
    #         "buttons_list": None,
    #         "fields_list": None,
    #         "resources_list": None
    #     }
    #     response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('prev')
    #     response["resources_list"] = copy.deepcopy(self.resources_list).remove('/prev')
    #     return response
    #
    # def close(self):
    #     element = self.browser.find_elements_by_class_name("close")
    #     element[0].click()
    #     # return copy.deepcopy(self.gallery_options).remove('close')
    #     response = {
    #         "buttons_list": None,
    #         "fields_list": None,
    #         "resources_list": None
    #     }
    #     response["buttons_list"] = copy.deepcopy(self.gallery_options).remove('close')
    #     response["resources_list"] = copy.deepcopy(self.resources_list).remove('/close')
    #     return response

    # def get_home_buttons(self):
    #     # elements = self.find_elements_by_tag_name("input")
    #     elements = self.find_element(By.XPATH, '//*[contains(@id, "button-")]')
    #     print "in home buttons dropbox"
    #     return [item.get_attribute("value").encode('utf-8') for item in elements]
    #     # // *[ @ id = "button-Dropbox"]
    #     # /html/body/div[1]/div/div[2]/div[2]/div[2]

    @classmethod
    def get_supported_resources(cls):
        return [
            "/connect-Dropbox", "/send-credentials-Dropbox", "/click-login-Dropbox",
            "/accept-authorization-Dropbox", "/deny-authorization-Dropbox",
            "/input-search-Dropbox", "/click-search-Dropbox"]
