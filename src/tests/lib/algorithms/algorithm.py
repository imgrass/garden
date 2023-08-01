from enum import Enum
from imgrass_horizon.lib.algorithms.red_black_tree import (
    Color, Direction, RBNode, RBTreeException, RedBlackTree,
    StepRecorder as RBTreeStepRecorderBase
)
from logging import getLogger
from yaml import safe_load as load_yaml


LOG = getLogger(__name__)


class StepRecorder(RBTreeStepRecorderBase):

    def __init__(self):
        self.steps = []

    def init_tree(self):
        self.steps.append(('set_as', 'root'))

    def search_node(self, key, direction: Direction, finished=False):
        self.steps.append(('search', key, direction.name.lower()))
        if finished:
            self.steps.append(('set_as', 'leaf'))

    def match_node(self, key):
        self.steps.append(('match', key))

    def unmatch_node(self):
        self.steps.append(('unmatch', ))

    def fixup_tree(self, myself: RBNode, parent: RBNode, grandparent: RBNode,
                   uncle: RBNode):
        directions = None
        direction_mapping = {
            Direction.LEFT: 'L',
            Direction.RIGHT: 'R'
        }
        direction = direction_mapping[parent.from_direction] + \
                    direction_mapping[myself.from_direction]

        if uncle.color == Color.RED:
            self.steps.append(('fixup', 'red-uncle', direction))
        else:
            self.steps.append(('fixup', 'black-uncle', direction))

    def blacken_root_node(self):
        self.steps.append(('fixup', 'red-root', ))

    def reset(self):
        self.steps = []

    @property
    def is_empty(self):
        return len(self.steps) == 0

    @property
    def next_step(self):
        if not self.steps:
            return None

        return self.steps.pop(0)

    @property
    def left_steps(self):
        return self.steps


class Step(object):

    class Behavior(Enum):
        set_as = 1
        search = 2
        fixup = 3
        match = 4
        unmatch = 5

    def __init__(self, behavior, data):
        assert isinstance(behavior, self.Behavior)

        self._behavior = behavior
        self._data = data
        self._validate()

    @classmethod
    def parse_from_desc(cls, behavior: str, data):
        if behavior in ('as', ):
            return cls(cls.Behavior.set_as, data)
        elif behavior in ('search', 's'):
            return cls(cls.Behavior.search, data)
        elif behavior in ('match', 'm'):
            return cls(cls.Behavior.match, data)
        elif behavior in ('unmatch', 'um'):
            return cls(cls.Behavior.unmatch, data)
        elif behavior in ('fixup', 'f'):
            return cls(cls.Behavior.fixup, data)
        else:
            assert (behavior, data) and False

    @property
    def description(self):
        return getattr(self, f'_describe_{self._behavior.name}')()

    def _describe_set_as(self):
        return f'Set value as {self._set_as_type}'

    def _describe_search(self):
        return f'Search under {self._search_direction} branch of node ' \
               f'{self._search_key}'

    def _describe_fixup(self):
        if self._fixup_type == 'red-root':
            return f'Fixup tree, found root node is red'
        return f'Fixup tree, found {self._fixup_type} with ' \
               f'{self._fixup_direction}'

    def _describe_match(self):
        return f'Match key {self._match_key}'

    def _describe_unmatch(self):
        return f'Unmatched'

    def _validate(self):
        getattr(self, f'_validate_{self._behavior.name}')()

    def _validate_set_as(self):
        assert self._data in ('root', 'leaf')
        self._set_as_type = self._data

    def _validate_search(self):
        direction = self._data[-2:]

        if direction == '->':
            self._search_direction = 'right'
        elif direction == '<-':
            self._search_direction = 'left'
        else:
            assert (direction, self._data) and False

        key = self._data[:-2].strip(' ')
        assert key != ''
        self._search_key = int(key)

    def _validate_match(self):
        assert self._data != ''
        self._match_key = int(self._data)

    def _validate_unmatch(self):
        assert self._data == ''

    def _validate_fixup(self):
        if ' ' not in self._data:
            fixup_type = self._data
            attribute = ''
        else:
            fixup_type = self._data[:self._data.find(' ')]
            attribute = self._data[self._data.find(' '):].strip(' ')

        if fixup_type == 'red-root':
            self._fixup_type = 'red-root'
            if attribute:
                assert (self._behavior.name, self._data) and False
        elif fixup_type in ('red-uncle', 'red-uncle', 'black-uncle'):
            self._fixup_type = fixup_type
            assert attribute in ('RR', 'RL', 'LL', 'LR')
            self._fixup_direction = attribute
        else:
            assert (self._behavior.name, self._data) and False

    def match(self, actual_step):
        actual_action = actual_step[0]
        assert actual_action == self._behavior.name

        self._actual_step = actual_step
        getattr(self, f'_match_{self._behavior.name}')()

    def _match_set_as(self):
        node_type = self._actual_step[1]
        assert self._set_as_type == node_type

    def _match_search(self):
        key = self._actual_step[1]
        direction = self._actual_step[2]

        assert key == self._search_key and direction == self._search_direction

    def _match_match(self):
        key = self._actual_step[1]

        assert key == self._match_key

    def _match_unmatch(self):
        ...

    def _match_fixup(self):
        actual_action = self._actual_step[1]

        if self._fixup_type == 'red-root':
            assert self._fixup_type == actual_action
            return

        directions = self._actual_step[2]
        assert self._fixup_type == actual_action and \
               directions == self._fixup_direction


class Action(object):

    class Behavior(Enum):
        search = 1
        insert = 2
        delete = 3

    def __init__(self, behavior, data):
        assert isinstance(behavior, self.Behavior)
        assert data is not None

        self._behavior = behavior
        self._key = data
        self._steps = []

    @classmethod
    def parse_from_desc(cls, desc: str, data):
        assert data is not None

        if desc in ('search', '/'):
            return cls(cls.Behavior.search, data)
        elif desc in ('insert', '+'):
            return cls(cls.Behavior.insert, data)
        elif desc in ('delete', '-'):
            return cls(cls.Behavior.delete, data)
        else:
            assert (desc, data) and False

    def register_step(self, step: Step):
        assert isinstance(step, Step)
        self._steps.append(step)

    @property
    def description(self):
        return f'{self._behavior.name} value {self._key}'

    @property
    def behavior(self):
        return self._behavior

    @property
    def key(self):
        return self._key

    @property
    def steps(self):
        return self._steps


class AlgorithmStepFollower(object):

    def __init__(self, behaviors_yml, algorithm_imp: RedBlackTree,
                 step_recorder: StepRecorder):
        assert isinstance(algorithm_imp, RedBlackTree)

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
