from . import APIBase


class RootController(object):

    def get(self):
        return 'Hello world'


class Root(APIBase):

    @property
    def controller(self):
        return RootController()

    @property
    def url(self):
        return '/'

    def define_actions_mapping(self):
        self.add_entry('GET', self.controller.get)
