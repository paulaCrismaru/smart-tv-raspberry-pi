import copy
import selenium.common.exceptions
import time

from selenium.webdriver.common.by import By

from cloud_services_providers.base import BaseNavigator


class GdriveNavigator():
    name = "gdrive"

    service_auth_url = "https://accounts.google.com/ServiceLogin?" # "https://www.dropbox.com/1/oauth2/authorize?"
    service_auth_cookie = "ACCOUNT_CHOOSER" # "cookie_notif"
    service_login_form_css_selector = None # ".clearfix.credentials-form.login-form"
    service_email_field_id = "//*[@id='Email']" # ".text-input-input.autofocus"
    service_password_field_id = "//*[@id='Passwd']"  # "login_password"
    service_login_button_css_selector = None # ".login-button.button-primary"
    service_authorize_form_id = "gaia_firstform"
    service_allow_button_name = None # "allow_access"
    service_deny_button_name = None # "deny_access"
    service_authorize_box_id = None # "auth"

    def __init__(self, browser, conf=None):
        self.browser = browser
        base = BaseNavigator()
        for variable_name in base.get_class_variables():
            if variable_name == "login_app_button":
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name.title())
            else:
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name)
            setattr(GdriveNavigator, variable_name, variable_value)

    def do_login_service(self, email=None, password=None):
        response = {
            "buttons_list": ['sign-in'],
            "resources_list": ['/click-login-dropbox']
        }
        form = self.browser.find_element_by_id(self.service_authorize_form_id)
        try:
            if email is not None:
                self.insert_in_login_field(
                    'Email',
                    "//*[@id='Email']",
                    email)
                self.click_button("gaia_firstform", "signIn")
        except selenium.common.exceptions.NoSuchElementException as e:
            raise e
        time.sleep(0.5)
        if password is not None:
            self.insert_in_login_field(
                "Passwd",
                "//*[@id='Passwd']",
                password)
            # self.click_button("gaia_firstform", "signIn")
            # form.find_element_by_id(self.service_email_field_id)
            # form = self.browser.find_element_by_id("Passwd")
            # element = form.find_element(By.XPATH, "//*[@id='Passwd']")
            # element.clear()
            # element.send_keys("adadssad")
            # self.click_button("gaia_firstform", "signIn")
        response["buttons_list"] = ['sign-in']
        response["buttons_list"] = ['/click-login-gdrive']
        return response

    def insert_in_login_field(self, element_id, element_xpath, data):
        form = self.browser.find_element_by_id(element_id)
        element = form.find_element(By.XPATH, element_xpath)
        element.clear()
        element.send_keys(data)

    def click_login_service(self):
        # try:
        response = {
            "buttons_list": ['sign-in'],
            "resources_list": ['/click-login-dropbox']
        }
        form = self.browser.find_element_by_class_name("form-panel.second")
        button = form.find_element_by_name("signIn")
        button.click()
        response["buttons_list"] = ["allow", "deny"]
        response["resources_list"] = [
            "/accept-authorization-gdrive",
            "/deny-authorization-gdrive"]
        return response
        # except:
        #     self.click_button("gaia_firstform","signIn")
        #     return ["sign-in"]

    def accept_authorization(self):
        try:
            form = self.browser.find_element_by_class_name("modal-dialog-buttons.button_container")
            button = form.find_element_by_id("submit_approve_access")
            button.click()
            # self.click_button(self.service_authorize_box_id, self.service_allow_button_name)
        except:
            raise

    def deny_authorization(self):
        try:
            form = self.browser.find_element_by_class_name("modal-dialog-buttons.button_container")
            button = form.find_element_by_id("submit_deny_access")
            button.click()
            # self.click_button(
            #     self.service_authorize_box_id,
            #     self.service_deny_button_name)
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
            "resources_list": None,
            "fields_list": None
        }
        time.sleep(2)
        if self.browser.current_url.encode('utf-8').startswith(self.service_auth_url):
            if self.browser.get_cookie("ACCOUNT_CHOOSER"):
                response["buttons_list"] = ["sign-in"]
                response["fields_list"] = ["password"]
                response["resources_list"] = ["/click-login-gdrive"]
                    # is not None\
                    # or self.browser.get_cookie("bjar") is not None:
            # if self.browser.current_url.contains("auth-finish"):
            #     return ['accept-authorization-gdrive', 'deny-authorization-gdrive'], None
            else:
                # return ['next'], ['email']
                response["buttons_list"] = ["next"]
                response["fields_list"] = ["email"]
                response["resources_list"] = ["/click-login-gdrive"]
        return response

    @classmethod
    def get_supported_resources(cls):
        return [
            "/connect-gdrive", "/send-credentials-gdrive", "/click-login-gdrive",
            "/accept-authorization-gdrive", "/deny-authorization-gdrive",
            "/input-search-gdrive", "/click-search-gdrive"]
