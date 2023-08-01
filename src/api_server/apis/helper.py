from . import APIBase


class HelperController(object):

    def get(self):
        return 'help ....'


class Helper(APIBase):

    @property
    def controller(self):
        return HelperController()

    @property
    def url(self):
        return '/help/'

    def define_actions_mapping(self):
        self.add_entry('GET', self.controller.get)
