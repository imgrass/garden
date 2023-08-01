from . import APIBase


class TaskController(object):

    def get(self):
        return 'help ....'

    def index(self):
        return 'help ....'


class Task(APIBase):

    @property
    def controller(self):
        return TaskController()

    @property
    def url(self):
        return '/task/'

    def define_actions_mapping(self):
        self.add_entry('GET', self.controller.get)


class Tasks(APIBase):

    @property
    def controller(self):
        return TaskController()

    @property
    def url(self):
        return '/tasks/'

    def define_actions_mapping(self):
        self.add_entry('GET', self.controller.index)
