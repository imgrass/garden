from .algorithm import AlgorithmStepFollower, StepRecorder
from __data__ import fake_red_black_tree as fake_tree
from imgrass_horizon.lib.algorithms.red_black_tree import (
    RBTreeException, RedBlackTree
)
from logging import getLogger
from pytest import raises


LOG = getLogger(__name__)


class TestRedBlackTree(object):

    def test_insert(self):
        step_recorder = StepRecorder()
        algorithm_imp = RedBlackTree(step_recorder=step_recorder)
        follower = AlgorithmStepFollower(fake_tree.INSERTION_STEPS,
                                         algorithm_imp, step_recorder)
        follower.run()

    def test_allow_insert_duplicate_key(self):
        step_recorder = StepRecorder()
        algorithm_imp = RedBlackTree(step_recorder=step_recorder)
        follower = AlgorithmStepFollower(fake_tree.INSERT_DUPLICATE_KEY_STEPS,
                                         algorithm_imp, step_recorder)
        follower.run()

    def test_disallow_insert_duplicate_key(self):
        step_recorder = StepRecorder()
        algorithm_imp = RedBlackTree(allow_dup_keys=False,
                                     step_recorder=step_recorder)
        follower = AlgorithmStepFollower(fake_tree.INSERT_DUPLICATE_KEY_STEPS,
                                         algorithm_imp, step_recorder)
        with raises(RBTreeException) as exc_info:
            follower.run()

        dup_key = follower.actions[-1].key
        assert exc_info.value.info.dup_key == dup_key

    def test_delete(self):
        ...

    def test_search_matched(self):
        step_recorder = StepRecorder()
        algorithm_imp = RedBlackTree(step_recorder=step_recorder)
        follower = AlgorithmStepFollower(fake_tree.SEARCH_400_STEPS,
                                         algorithm_imp, step_recorder)
        follower.run()

    def test_search_unmatched(self):
        step_recorder = StepRecorder()
        algorithm_imp = RedBlackTree(step_recorder=step_recorder)
        follower = AlgorithmStepFollower(fake_tree.SEARCH_450_STEPS,
                                         algorithm_imp, step_recorder)
        follower.run()


    def test_pre_order_traversal(self):
        ...

    def test_in_order_traversal(self):
        ...

    def test_post_order_traversal(self):
        ...
