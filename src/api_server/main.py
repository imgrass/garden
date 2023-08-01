from .wsgi import application
from ..lib.service import ManagerBase, Service
from eventlet import listen
from eventlet.wsgi import server
from sys import exit as sys_exit


class ApiManager(ManagerBase):

    def __init__(self):
        super().__init__()

    def start_wsgi_server(self):
        server(listen(('', 8090)), application)

    def do_run(self):
        self.let_service('new_greenlet')(self.start_wsgi_server)


def main():
    Service(ApiManager(), pool_size=0).run()


if __name__ == '__main__':
    sys_exit(main())
