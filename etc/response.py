class Response:
    def __init__(self, code, current_page, buttons_list, fields_list, resources_list, menu=None, message=None):
        self.code = code
        self.current_page = current_page
        self.buttons = buttons_list
        self.fields = fields_list
        self.menu = menu
        self.message = message
        self.resources_list = resources_list

