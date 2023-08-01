from .exception import ExceptionBase, ExceptionInfo, register_exception
from enum import Enum
from typing import Optional, Type


class FollowerSyntaxError(ExceptionBase):

    @register_exception
    def function_not_defined(info: ExceptionInfo, line, char):
        info.tell_me('The function is not defined, expecting the character '
                     f'"." not "{char}". The error occurred in line "{line}"')

    @register_exception
    def invalid_func_name(info: ExceptionInfo, reason, line, char):
        info.tell_me('An invlid function name was found while parsing '
                     'character "{char}" in line "{line}" because {reason}')


class StepRecorderBase(object):
    '''
    The implementation of various algorithms is generally complicated. In order
    to facilitate the debugging, we hope to recored the key steps of the
    algorithm, so that we can see whether the program is strictly following the
    expected steps.
    '''

    def __init__(self, inst_algorithm: 'AlgorithmBase'):
        assert isinstance(inst_algorithm, AlgorithmBase)

        self.inst_algorithm = inst_algorithm


class AlgorithmBase(object):

    step_recorder: Optional[StepRecorderBase] = None
    enable_step_recorder: bool = False

    def __init__(self, step_recorder=None):
        assert step_recorder is None \
                or isinstance(step_recorder, StepRecorderBase)

        if step_recorder:
            self.step_recorder = step_recorder

    def open_step_recorder(self):
        if self.step_recorder is None:
            raise SyntaxError(
                'The step recoreder of the algorithm class '
                f'{self.__class__.__name__} is None, so the step recording '
                'function can not be enabled for this algorithm class. Please '
                'check whether the step recoreder is set when the class is '
                'initialized.')
        self.enable_step_recorder = True

    def close_step_recorder(self):
        self.enable_step_recorder = False


class FollowerEntrypoint(object):
    ...


class FollowerAST(object):
    '''
    This class is responsible for parsing the step follower source file written
    by the user into instructions. We first limit the functions that the step
    follower can provide:

        - Only supports sequential execution, does not support conditional and
          loop statements

        - Variables are not supported

        - Each statement is a function whose format is as follows:
            .{function} [arguments]
          or
            .{function}:
                [arguments]

          The first letter of the function must be capitalized.
    '''

    class Instructions(object):

        def __init__(self):
            self._data = []

        def add_function(self, name):
            ...

        def add_argument(self, word):
            ...

    class Stack(object):

        class Action(Enum):

            wait_function = 1
            wait_argument = 2
            wait_string = 3

        def __init__(self):
            self._data = []

        def wait_function(self):
            for idx in 
            self._data.append((self.Action.wait_function, 1))

        @property
        def top(self):
            return self._data[-1]

        @property
        def isempty(self):
            return not bool(self._data)

    def __init__(self, source_code: str, entrypoints: FollowerEntrypoint):
        assert isinstance(source_code, str)
        assert isinstance(entrypoints, FollowerEntrypoint)

        self._source_code = source_code
        self._entrypoints = entrypoints

        self._instructions = self.Instructions()

        self._special_symbols = {
            '\'': ,
            '"': ,
            '(': ,
            ')': ,
            '.': ,
            ',': ,
            '\\': ,
        }

        self._stack = self.Stack()

    def parser(self):
        for char in self._source_code:
            ...




class AlgorithmStepFollower(object):
    '''
    In order to verify the correctness of the algorithm, we want to let the
    algorithm perform a specific action list, and then compare their acutal
    steps with the expected.

    +-----------------------------+
    |                             |
    | - Operation ----------------\--o      For-Loop
    |   Expected Steps:           |   \      +----------+
    |     +--------------------+  |    ----->| Executor |
    |     | - Action arguments |  |          +----------+
    |     | ...                |  |               |
    |     +--------------------+<-/---------------o Actual Steps
    | ...                         |
    -----------------------------+

    '''

    def __init__(self, behaviors_yml, algorithm_imp: AlgorithmBase,
                 step_recorder: StepRecorderBase):
        assert isinstance(algorithm_imp, RedBlackTree)
        assert isinstance()

        self._behaviors = []
        self._algorithm_imp = algorithm_imp
        self._step_recorder = step_recorder

        for behavior in load_yaml(behaviors_yml):
            for action, steps in behavior.items():
                _action = Action.parse_from_desc(
                    action[:action.find(' ')],
                    int(action[action.find(' '):].strip(' '))
                )
                self._behaviors.append(_action)

                for step in steps:
                    if ' ' in step:
                        _action.register_step(Step.parse_from_desc(
                            step[:step.find(' ')],
                            step[step.find(' '):].strip(' ')
                        ))
                    else:
                        _action.register_step(Step.parse_from_desc(step, ''))

        self._algorithm_imp.open_step_recorder()

    def run(self):
        for action in self._behaviors:
            self._step_recorder.reset()
            LOG.debug(f'* Action: {action.description}')
            if action.behavior.name == 'insert':
                getattr(self._algorithm_imp, action.behavior.name)(
                        action.key, None)
            else:
                getattr(self._algorithm_imp, action.behavior.name)(action.key)

            for expected_step in action.steps:
                expected_step: Step
                actual_step = self._step_recorder.next_step
                assert ('Possible reason',
                        '1. Expected steps are less than actual steps',
                        '2. Function "step recorder" is not opened') and \
                       actual_step is not None

                try:
                    expected_step.match(actual_step)
                    LOG.debug(f'  - Step: {expected_step.description}')
                except AssertionError as e:
                    assert (f'Action: {action.description}',
                            f'Expected Step: {expected_step.description}',
                            f'Actual Step: {actual_step}', e) and False

            if not self._step_recorder.is_empty:
                assert ('A few more steps than expected', action.description,
                        self._step_recorder.left_steps) and False

    @property
    def actions(self):
        return self._behaviors

    @property
    def description(self):
        description = []

        for behavior in self._behaviors:
            description.append(behavior.description)
            for step in behavior.steps:
                description.append(step.description)

            description.append('')

        return '\n'.join(description)
