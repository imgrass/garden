from .singleton import ABCSingletonMix, Singleton
from abc import ABC, abstractmethod, abstractproperty
from eventlet import GreenPool, sleep, spawn_n
from eventlet.greenthread import GreenThread
from functools import partialmethod, wraps
from multiprocessing import cpu_count, Pool
from queue import Queue
from typing import Any, Callable, Dict, Optional


from logging import getLogger
LOG = getLogger(__name__)


class ManagerBase(ABCSingletonMix):
    '''
    The <<ManagerBase>> class is designed to handle business logic. User need
    to implement their own <<Manager>> class and inherited from this class.
    For example:

        >>> class Manager(ManagerBase):
        >>> 
        >>>     def __init__(self):
        >>>         super().__init__()
        >>> 
        >>>     def do_run(self):
        >>>         def test(a, b, wait=0):
        >>>             if wait > 0:
        >>>                 sleep(wait)
        >>>             print(f'Run test {a} ... {b}')
        >>>             return f'{a}+{b}'
        >>>         self.let_service('new_greenlet')(test, (1, 2), {'wait': 1})
        >>>         self.let_service('new_greenlet')(test, (3, 4), {'wait': 2})
        >>>         task3 = self.let_service('new_greenlet')(test, (1, 6), {})
        >>>         self.let_service('new_greenlet')(test, (1, 8), {})
        >>> 
        >>>         print(f'task3 is {task3.wait()}')
    '''

    # The task split by the manager class needs to be executed by the serivce
    # class, but itself is an attribute of the service class, so this needs to
    # borrow this mapping relationship to transparently transmit part of the
    # service's capabilities
    SERVICE_HANDLERS: Dict[str, Callable[[], Any]]

    def __init__(self):
        self._loop_done = False
        self.SERVICE_HANDLERS = {}

    def register_service_handler(self, name: str,
                                 service_method: Callable[[], Any]):
        self.SERVICE_HANDLERS[name] = service_method

    def let_service(self, action: str) -> Callable[[], Any]:
        return self.SERVICE_HANDLERS[action]

    def run(self):
        self.do_run()
        self._loop_done = True

    def do_finish(self):
        ...

    @abstractmethod
    def do_run(self):
        ...

    @property
    def loop_done(self):
        return self._loop_done


class TaskBase(ABC):

    data: dict

    @abstractproperty
    def ready(self) -> bool:
        ...

    @property
    def cb(self) -> Callable[[], Any]:
        return self._cb

    @property
    def args(self) -> tuple:
        return self._args

    @property
    def kwargs(self) -> dict:
        return self._kwargs

    @property
    def as_greenlet(self):
        return isinstance(self, TaskLocalGreenlet)


class TaskLocalGreenlet(TaskBase):

    def __init__(self, cb: Callable[[], Any], args: tuple, kwargs: dict):

        self._data = {
            'started': False,
            'ended': False,
            'result': None
        }

        @wraps(cb)
        def cb_wrapper():
            self._data['started'] = True
            result = cb(*args, **kwargs)
            self._data['result'] = result
            self._data['ended'] = True

        self._cb = cb_wrapper
        self._args = args
        self._kwargs = kwargs

    @property
    def ready(self) -> bool:
        if self._data['ended']:
            return True
        return False

    @property
    def result(self):
        return self._data['result']

    def wait(self):
        while True:
            if self.ready:
                break
            sleep()

        return self.result



class Service(Singleton):

    MIN_POOL_SIZE = 2
    CPU_RESERVED_FOR_SYSTEM = 1
    MAX_GREENLET_SIZE = 10000

    def __init__(self, manager: ManagerBase, pool_size=None, max_greenlets=0):
        assert isinstance(manager, ManagerBase)
        self.manager = manager
        self.manager.register_service_handler('new_greenlet',
                                              self.new_greenlet)

        actual_pool_size = self.get_pool_size(pool_size)
        if actual_pool_size:
            self.pool = Pool(actual_pool_size)
        else:
            self.pool = None

        self.task_queue = Queue()

        if max_greenlets == 0:
            self.gpool = GreenPool(self.MAX_GREENLET_SIZE)
        elif max_greenlets > 0:
            self.gpool = GreenPool(max_greenlets)
        else:
            raise TypeError(f'The max greenlets {max_greenlets} < 0')

    def get_pool_size(self, pool_size):
        assert pool_size is None or pool_size >= 0

        if pool_size is None:
            cpus = cpu_count()
            return max(cpus-self.CPU_RESERVED_FOR_SYSTEM, self.MIN_POOL_SIZE)

        if pool_size > 0:
            return max(pool_size, self.MIN_POOL_SIZE)

        return 0

    def run(self):

        spawn_n(self.manager.run)

        while True:
            while True:
                if self.task_queue.empty():
                    break

                task: TaskBase = self.task_queue.get()
                if task.as_greenlet:
                    self.gpool.spawn_n(task.cb)

                elif task.type == TaskType.SUBPROCESS_GREENLET:
                    ...
                elif task.type == TaskType.COMMANDLINE:
                    ...
                elif task.type == TaskType.PTY:
                    ...
                else:
                    raise TypeError(f'Unacceptable task type <{task.type}>')

            if self.manager.loop_done:
                break

            sleep()

        self.gpool.waitall()

        self.manager.do_finish()

    def __del__(self):
        if self.pool:
            self.pool.close()

    def new_greenlet(self, cb: Callable[[], Any], args: Optional[tuple]=None,
                     kwargs: Optional[dict]=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        task = TaskLocalGreenlet(cb, args, kwargs)
        self.task_queue.put(task)
        return task
