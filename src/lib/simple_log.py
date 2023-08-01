# The standard logging library feels too cumbersome to use, so a simple library
# is implemented here
from .singleton import Singleton
from abc import ABC, abstractmethod
from enum import Enum


class Level(Enum):
    debug = 1
    info = 2
    warning = 3
    error = 4


class HandlerBase(object):
    __CLOSED__ = False
    __REMOVED__ = False

    def __init__(self, level, formatter=None):
        assert isinstance(level, Level)

        self.level = level
        self.formatter = Formatter(formatter)

    def close(self):
        self.__CLOSED__ = True

    @property
    def closed(self):
        return self.__CLOSED__

    def open(self):
        self.__CLOSED__ = False

    @property
    def opened(self):
        return not self.__CLOSED__

    def remove(self):
        self.__REMOVED__ = True

    @property
    def removed(self):
        return self.__REMOVED__

    def is_enough_level(self, level):
        assert isinstance(level, Level)
        return level.value >= self.level.value

    @abstractmethod
    def record(self, level, fmt, **kwargs):
        ...


class FileHandler(HandlerBase):

    def __init__(self, level, file, formatter=None):
        if 
        self.file = file
        super().__init__(level, formatter=formatter)

    def record(self, level, fmt, **kwargs):
        ...


class StreamHandler(HandlerBase):

    def __init__(self, level, formatter=None):
        super().__init__(level, formatter=formatter)

    def record(self):
        ...


class Formatter(object):

    class Type(Enum):
        message = 1
        level = 2
        path = 3
        line = 4
        now = 5
        pid = 6

    def __init__(self, template):
        self.template = template

    def decorate(self, level, message):
        return f'TODO: {message}'


format_type = Formatter.Type


class Log(Singleton):

    def __init__(self):
        # Store instances of all log handler classes
        # {
        #     StreamHandler: [ hdl_stream ],
        #     FileHandler: [ hdl_file1, hdl_file2 ]
        # }
        self._handlers = {}

    def add_handler(self, hdl_cls, *args, **kwargs):
        assert issubclass(hdl_cls, HandlerBase)

        hdls = self._handlers.setdefault(hdl_cls, [])
        hdl = hdl_cls(*args, **kwargs)
        hdls.append(hdl)
        return hdl

    def find_handlers(self):
        ...

    @property
    def handlers(self):
        ...

    @property
    def opened_handler(self):
        ...

    def _record(self, level, fmt, **kwargs):
        empty_handler_cls = []

        for hdl_cls, hdls in self._handlers.items():
            idx = 0
            while idx < len(hdls):
                hdl: HandlerBase = hdls[idx]
                if hdl.removed:
                    hdls.pop(idx)
                if hdl.opened:
                    hdl.record(level, fmt, **kwargs)
                idx += 1

            if not hdls:
                empty_handler_cls.append(hdl_cls)

        for hdl_cls in empty_handler_cls:
            self._handlers.pop(hdl_cls)

    debug = partialmethod(_record, Level.debug)
    info = partialmethod(_record, Level.info)
    warning = partialmethod(_record, Level.warning)
    error = partialmethod(_record, Level.error)


if __name__ == '__main__':
    FT = format_type
    log = Log()
    log.add_handler(StreamHandler, Level.info,
                    formatter=f'[{FT.level}]: {FT.message}')
    log.add_handler(FileHandler, Level.debug, '/tmp/b.log',
                    formatter=f'{FT.level} -> {FT.message}')

    log.info('Hello world')
    log.debug('lalala...')
