from .routes import API_ROUTES
from flask import Flask
from logging import basicConfig, getLogger
from os.path import join
from oslo_config.cfg import CONF
from socketio import Server, WSGIApp
#import engineio
#import socketio


__all__ = ['application']


LOG = getLogger(__name__)


class SunriseApplication(Flask):
    def __init__(self):
        super().__init__(__name__)

        for url, action_maps in API_ROUTES.items():
            for action, handler in action_maps.items():
                endpoint = f'{handler.__module__}.' \
                           f'{handler.__self__.__class__.__name__}:' \
                           f'{handler.__name__}'
                self.route(url, methods=[action], endpoint=endpoint)(handler)


wsgi_app = SunriseApplication()


class WsgiApplication(WSGIApp):
    def __init__(self, wsgi_app, static_files=None,
                 socketio_path='socket.io'):
        # Config('/etc/sunrise')

        # cfg_log = CONF['sunrise-log']
        # basicConfig(level=get_log_level(cfg_log.log_python_level),
        #             filename=join(CONF.dir_log, cfg_log.log_python),
        #             format=cfg_log.log_python_format)

        # sio_logger = getLogger(socketio.__name__)
        # sio_logger.setLevel(get_log_level(cfg_log.log_python_level))
        # engineio_logger = getLogger(engineio.__name__)
        # engineio_logger.setLevel(get_log_level(cfg_log.log_python_level))

        # socketio_app = Server(logger=sio_logger,
        socketio_app = Server()
        if socketio_app.async_mode != 'eventlet':
            raise Exception("only support eventlet")

        @socketio_app.event
        def disconnect(sid):
            LOG.info('%s: disconnecting', sid)

        @socketio_app.event
        def connect(sid, environ, *args, **kwargs):
            LOG.info('%s: connecting', sid)

        super().__init__(socketio_app, wsgi_app=wsgi_app,
                         static_files=static_files,
                         socketio_path=socketio_path)


application = WsgiApplication(wsgi_app)
