from eventlet import sleep
from imgrass_horizon.lib.service import ManagerBase, Service
from logging import getLogger
from multiprocessing import Process, Queue
from os import getpid, getppid
from sys import exit


LOG = getLogger(__name__)


class Manager(ManagerBase):

    def __init__(self, queue, tasks):
        super().__init__()
        self.q = queue
        self.tasks = tasks

    def do_run(self):

        def test(task, wait=0):
            if wait > 0:
                sleep(wait)
            self.q.put(task)

        started_tasks = {}
        while len(started_tasks) < len(self.tasks):
            sleep()
            for task in self.tasks:
                sleep()
                if task.task in started_tasks:
                    continue

                if not task.wait_finished_tasks:
                    started_tasks[task.task] = \
                        self.let_service('new_greenlet')(
                            test, (task.task, ), {'wait': task.wait})
                    continue

                all_tasks_finished = True
                for wait_task in task.wait_finished_tasks:
                    sleep()
                    if wait_task not in started_tasks or \
                            not started_tasks[wait_task].ready:
                        all_tasks_finished = False
                        break

                if all_tasks_finished:
                    started_tasks[task.task] = \
                        self.let_service('new_greenlet')(
                            test, (task.task, ), {'wait': task.wait})


class TestManager(object):


    class Task(object):

        def __init__(self, task, wait=0, wait_finished_tasks=None):
            self.task = task
            self.wait = wait
            self.wait_finished_tasks = wait_finished_tasks or []


    def test_sched_green_tasks(self):

        tasks = (
            self.Task('task1', wait=2),
            self.Task('task2'),
            self.Task('task3', wait=1),
            self.Task('task4', wait_finished_tasks=['task2', 'task3'])
        )
        expected_result = ['task2', 'task3', 'task4', 'task1']

        queue = Queue()

        def worker():
            Service(Manager(queue, tasks)).run()

        def dequeue():
            while not queue.empty():
                actual_task = queue.get()
                expected_task = expected_result.pop(0)
                LOG.info(f'Assert expected task ({expected_task}) == actual '
                         f'task ({actual_task})')
                assert actual_task == expected_task

        process = Process(target=worker)
        process.start()

        while True:

            if not process.is_alive():
                if queue.empty():
                    assert len(expected_result) == 0
                    break
                dequeue()
                break

            if not queue.empty():
                dequeue()
