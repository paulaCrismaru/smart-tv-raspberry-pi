from selenium.webdriver.common.by import By

from cloud_services_providers.base import BaseNavigator
import time

class YoutubeNavigator(BaseNavigator):

    app_url = "https://www.youtube.com"
    name = "Youtube"
    xpath_input = '//*[@id="masthead-search-term"]'
    search_button = '//*[@id="search-btn"]'


    def __init__(self, browser, conf):
        self.browser = browser
        base = BaseNavigator()
        for variable_name in base.get_class_variables():
            if variable_name == "login_app_button":
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name.title())
            else:
                variable_value = "%s-%s" % (getattr(BaseNavigator, variable_name), self.name)
            setattr(YoutubeNavigator, variable_name, variable_value)
        # YoutubeNavigator.process_conf(conf)
        self.current_search_results = None
        self.current_index = None


    @classmethod
    def add_variable(cls, name, value):
        setattr(YoutubeNavigator, name, value)

    @classmethod
    def process_conf(cls, conf):
        for item in conf.__dict__:
            if not item.startswith("__"):
                setattr(YoutubeNavigator, item, getattr(conf, item))

    @classmethod
    def get_input_field(cls):
        return cls.xpath_input

    @classmethod
    def get_search_button(cls):
        return cls.search_button

    def _send_key(self, key):
        element = self.browser.find_element(By.CLASS_NAME, "player-api")
        element.send_keys(key)

    def full_screen(self):
        print "face full screen"
        self._send_key("f")

    def play_pause(self):
        self._send_key("k")

    def send_input(self, data):
        element = self.browser.find_element(By.XPATH, self.get_input_field())
        element.clear()
        element.send_keys(data)

    def click_search_(self):
        element = self.browser.find_element(By.XPATH, self.get_search_button())
        element.click()

    @classmethod
    def is_current_provider(cls, url):
        if url.startswith(cls.app_url):
            return True
        return False

    def get_current_page_options(self):
        args = {
            "code": 200,
            "buttons_list": ["search"],
            "fields_list": ["search"],
            "resources_list": ["/click-search-Youtube"]
        }
        url = self.browser.current_url
        path = url.split(YoutubeNavigator.app_url)
        try:
            path.remove('')
        except:
            pass
        path = path[0]
        if path.startswith("/results"):
            args["buttons_list"] += ["next", "prev", "start"]
            args["resources_list"] += ["/next", "/prev", "/start"]
        elif path.startswith("/watch"):
            args["buttons_list"] += ["play", "pause", "full-screen", "exit-full-screen"]
            args["buttons_list"] += ["/play", "/pause", "/full-screen", "/exit-full-screen"]

        return args

    def handle_get(self, path):
        args = {
            "code": 200,
            "buttons_list": ["search"],
            "fields_list": ["search"],
            "resources_list": ["/click-search-Youtube"]
        }
        # path = self.browser.current_url.replace("https://www.youtube.com/", "")

        self.browser.get(path)
        current_url = self.browser.current_url.replace(YoutubeNavigator.app_url, "")
        if current_url.startswith("/watch"):
            buttons = ["pause", "play", "full-screen", "exit-full-screen"]
            resources = ["/pause", "/play", "/full-screen", "/exit-full-screen"]
            args["buttons_list"] += buttons
            args["resources_list"] += resources
        elif current_url.startswith("/results"):
            buttons = ["next", "prev", "start"]
            args["resources_list"] += ["/next", "/prev", "/start"]
            args["buttons_list"] += buttons
        return args

    def handle_post(self, path, data):
        args = {
            "code": 200,
            "buttons_list": ["search"],
            "fields_list": ["search"],
            "resources_list": ["/click-search-Youtube"]
        }
        if path == "/input-search-Youtube":
            print data
            print data[u'data']
            self.send_input(data[u'data'])
        elif path == "/click-search-Youtube":
            self.click_search_()
            time.sleep(1)
            self.compute_list()
            element = self.current_search_results[self.current_index]
            self.highlight(element)
        elif path == "/play" or path == "/pause":
            self.play_pause()
        elif path == "/full-screen" or path == "/exit-full-screen":
            self.full_screen()
        elif path == "/start":
            self.start_video()
        elif path == "/next":
            self.hover_next_video()
            args["buttons_list"] += ["next", "prev", "start"]
            args["resources_list"] += ["/next", "/prev", "/start"]
        elif path == "/prev":
            self.hover_previews_video()
            args["buttons_list"] += ["next", "prev", "start"]
            args["resources_list"] += ["/next", "/prev", "/start"]

        current_url = self.browser.current_url.replace(YoutubeNavigator.app_url, "")
        print current_url
        if current_url.startswith("/watch"):
            buttons = ["pause", "play", "full-screen", "exit-full-screen"]
            args["buttons_list"] += buttons
        elif current_url.startswith("/results"):
            buttons = ["next", "prev", "start"]
            args["buttons_list"] += buttons


        return args

    def hover_next_video(self):
        self.unhighlight(self.current_search_results[self.current_index])
        self.highlight(self.current_search_results[self.current_index + 1])
        self.current_index += 1

    def hover_previews_video(self):
        self.unhighlight(self.current_search_results[self.current_index])
        self.highlight(self.current_search_results[self.current_index - 1])
        self.current_index -= 1

    def compute_list(self):
        ol = self.browser.find_elements_by_class_name("item-section")
        self.current_search_results = ol[0].find_elements_by_xpath('li')
        self.current_index = 0

    def highlight(self, element):
        self.browser.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                    element, "border: 3px solid black;")

    def unhighlight(self, element):
        self.browser.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                    element, "border: none")

    def start_video(self):
        current_element = self.current_search_results[self.current_index]
        element = current_element.find_elements_by_xpath('div/div/div/a')
        url = element[0].get_attribute('href')
        self.browser.navigate_to(url)
