from ..algorithm import AlgorithmBase, StepRecorderBase
from ..exception import ExceptionBase, ExceptionInfo, register_exception
from enum import Enum
from typing import Callable, Optional, Type


class RBTreeException(ExceptionBase):

    @register_exception
    def insert_duplicated_key(info: ExceptionInfo, dup_key):
        info.tell_me('This Red-Black tree do not allow duplicated key '
                     f'{dup_key} to be inserted.')
        info.dup_key = dup_key

    @register_exception
    def no_key_found(info: ExceptionInfo, key):
        info.tell_me(f'Can not find key {key} in Reb-Black tree')
        info.key = key


class StepRecorder(StepRecorderBase):

    def init_tree(self):
        ...

    def search_node(self, current_node, insert_node):
        ...

    def match_node(self, node):
        ...

    def unmatch_node(self):
        ...

    def fixup_tree_black_parent(self, myself, parent):
        ...

    def fixup_tree(self, myself, parent, grandparent, uncle):
        ...


class Color(Enum):
    RED = 0
    BLACK = 1


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class RBNode(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left: 'RBNode' = None
        self.right: 'RBNode' = None
        self.color = Color.RED

        # root node do not need <from_direction> and parent
        self.parent: Optional['RBNode'] = None
        self.from_direction: Optional[Direction ]= None

    @classmethod
    def new_null_node(cls):
        nd_null = cls(None, None)
        nd_null.color = Color.BLACK
        return nd_null


class RedBlackTree(AlgorithmBase):

    RB_NODE_CLS: Type[RBNode]
    ND_NULL: RBNode
    ND_ROOT: RBNode

    def __init__(self, rb_node_cls: Type[RBNode]=RBNode, allow_dup_keys=True,
                 step_recorder: Optional[StepRecorder]=None):

        assert issubclass(rb_node_cls, RBNode)
        assert isinstance(allow_dup_keys, bool)
        assert step_recorder is None or isinstance(step_recorder, StepRecorder)
        super().__init__(step_recorder=step_recorder)

        self.allow_dup_keys = allow_dup_keys

        self.RB_NODE_CLS = rb_node_cls
        self.ND_ROOT = self.ND_NULL = RBNode.new_null_node()

    def insert(self, *args, **kwargs) -> RBNode:
        new_node = self.RB_NODE_CLS(*args, **kwargs)

        nil: RBNode = self.ND_NULL

        grandparent: RBNode
        parent: RBNode
        uncle: RBNode
        myself: RBNode = self.ND_ROOT

        # Insert a empty tree
        if self.ND_ROOT is nil:
            self.ND_ROOT = new_node
            self.ND_ROOT.color = Color.BLACK
            self.ND_ROOT.left = self.ND_NULL
            self.ND_ROOT.right = self.ND_NULL

            if self.enable_step_recorder:
                self.step_recorder.init_tree()

            return new_node

        # Find the insert point
        while True:
            if new_node.key <= myself.key:

                if not self.allow_dup_keys and new_node.key == myself.key:
                    raise RBTreeException.insert_duplicated_key(new_node.key)

                if myself.left is self.ND_NULL:
                    myself.left = new_node
                    new_node.from_direction = Direction.LEFT
                    break
                myself = myself.left

                if self.enable_step_recorder:
                    self.step_recorder.search_node(myself.parent.key,
                                                   Direction.LEFT)

            else:
                if myself.right is self.ND_NULL:
                    myself.right = new_node
                    new_node.from_direction = Direction.RIGHT
                    break
                myself = myself.right

                if self.enable_step_recorder:
                    self.step_recorder.search_node(myself.parent.key,
                                                   Direction.RIGHT)


        if self.enable_step_recorder:
            self.step_recorder.search_node(myself.key, new_node.from_direction,
                                           finished=True)

        parent = myself
        myself = new_node
        myself.color = Color.RED
        myself.parent = parent
        myself.left = myself.right = self.ND_NULL

        # Fixup the structure of red-black tree
        while True:
            parent = myself.parent
            if parent.color == Color.BLACK:
                break

            grandparent = parent.parent
            if parent.from_direction == Direction.LEFT:
                uncle = grandparent.right
            else:
                uncle = grandparent.left

            if self.enable_step_recorder:
                self.step_recorder.fixup_tree(myself, parent, grandparent,
                                              uncle)

            # ==> Uncle is black
            #
            # When the following situation occurs, after a ratation and color
            # adjustment, the node x moves up to the (P) node, and at this time
            # the x node changes to black, so the nature of red-black tree can
            # be fully satisfied, and it can be over at this point.
            #
            #             |                          |
            #          G (B)                    x P (B)
            #           /   \                      /   \
            #       P (R)   (B) U     ==>      M (R)   (R) G
            #        /   \  /  \                 / \   /  \
            #  x M (R)   3  4  5                1   2  3 (B) U
            #     /   \                                  / \
            #    1     2                                4   5
            #
            # 1<M<2<P<3<G<4<U<5                1<M<2<P<3<G<4<U<5
            #
            # This situation takes four forms, depending on the direction from
            # Grandparent to Parent and from Parent to Myself, but the general
            # idea is the same, only the details are a little different. Among
            # them, when the two directions are not the same, one more rotation
            # will be made to turn it into the same situation as shown below:
            #
            #               |                      |
            #               G                      G
            #        L     / \       ==>    L     / \
            #             P   U                x M   U
            #        R    \                 R   /
            #            x M                   P
            #
            #             (LR)                   (LL)
            #
            if uncle.color == Color.BLACK:
                if myself.from_direction == parent.from_direction:
                    parent.color = Color.BLACK
                    grandparent.color = Color.RED

                    if grandparent != self.ND_ROOT:
                        parent.parent = grandparent.parent
                        if grandparent.from_direction == Direction.LEFT:
                            grandparent.parent.left = parent
                            parent.from_direction = Direction.LEFT
                        else:
                            grandparent.parent.right = parent
                            parent.from_direction = Direction.RIGHT
                    else:
                        self.ND_ROOT = parent
                        parent.parent = None
                        parent.from_direction = None
                    grandparent.parent = parent

                    if parent.from_direction == Direction.LEFT:
                        grandparent.left = parent.right
                        grandparent.left.parent = grandparent
                        grandparent.left.from_direction = Direction.LEFT
                        parent.right = grandparent
                        grandparent.from_direction = Direction.RIGHT
                    else:
                        grandparent.right = parent.left
                        grandparent.right.parent = grandparent
                        grandparent.right.from_direction = Direction.RIGHT
                        parent.left = grandparent
                        grandparent.from_direction = Direction.LEFT

                else:
                    myself.color = Color.BLACK
                    grandparent.color = Color.RED

                    if grandparent != self.ND_ROOT:
                        myself.parent = grandparent.parent
                        if grandparent.from_direction == Direction.LEFT:
                            grandparent.parent.left = myself
                            myself.from_direction = Direction.LEFT
                        else:
                            grandparent.parent.right = myself
                            myself.from_direction = Direction.RIGHT
                    else:
                        self.ND_ROOT = myself
                        myself.parent = None
                        myself.from_direction = None
                    grandparent.parent = myself

                    if parent.from_direction == Direction.LEFT:
                        grandparent.left = myself.right
                        grandparent.left.parent = grandparent
                        grandparent.left.from_direction = Direction.LEFT

                        myself.right = grandparent
                        grandparent.from_direction = Direction.RIGHT

                        parent.right = myself.left
                        parent.right.parent = parent
                        parent.right.from_direction = Direction.RIGHT

                        myself.left = parent
                        parent.parent = myself
                        parent.from_direction = Direction.LEFT

                    else:
                        grandparent.right = myself.left
                        grandparent.right.parent = grandparent
                        grandparent.right.from_direction = Direction.RIGHT

                        myself.left = grandparent
                        grandparent.from_direction = Direction.LEFT

                        parent.left = myself.right
                        parent.left.parent = parent
                        parent.left.from_direction = Direction.LEFT

                        myself.right = parent
                        parent.parent = myself
                        parent.from_direction = Direction.RIGHT

                break

            # ==> Uncle is red
            #
            # When the following situation occurs, only the color adjustment
            # is needed. Then, adjust Myself node to the Grandparent node.
            # Since it is still a red node, it continues to enter the loop for
            # processing.
            #
            #             |                           |
            #          G (B)                     x G (R)
            #           /   \                       /   \
            #       P (R)   (R) U     ==>       P (B)   (B) U
            #        /   \  /  \                 /   \  /  \
            #  x M (R)   3  4  5             M (R)   3  4  5
            #     /   \                       /   \
            #    1     2                     1     2
            #
            # 1<M<2<P<3<G<4<U<5           1<M<2<P<3<G<4<U<5
            #
            else:
                parent.color = Color.BLACK
                uncle.color = Color.BLACK

                if grandparent == self.ND_ROOT:
                    if self.enable_step_recorder:
                        self.step_recorder.blacken_root_node()
                    break

                grandparent.color = Color.RED
                myself = grandparent

        return new_node

    def search(self, key) -> Optional[RBNode]:

        nd_current = self.ND_ROOT
        while True:
            if nd_current == self.ND_NULL:

                if self.enable_step_recorder:
                    self.step_recorder.unmatch_node()

                return None

            if key < nd_current.key:

                if self.enable_step_recorder:
                    self.step_recorder.search_node(nd_current.key,
                                                   Direction.LEFT)

                nd_current = nd_current.left
            elif key > nd_current.key:

                if self.enable_step_recorder:
                    self.step_recorder.search_node(nd_current.key,
                                                   Direction.RIGHT)

                nd_current = nd_current.right
            else:

                if self.enable_step_recorder:
                    self.step_recorder.match_node(nd_current.key)

                return nd_current

    def delete(self, key) -> bool:

        nil: RBNode = self.ND_NULL

        grandparent: RBNode
        parent: RBNode
        sibling: RBNode
        nephew_left: RBNode
        nephew_right: RBNode
        myself: RBNode = self.ND_ROOT

        nd_matched: RBNode

        # ==> Navigate to the node to be deleted
        while True:
            if myself == nil:
                return False

            if key < myself.key:
                myself = myself.left
            elif key > myself.key:
                myself = myself.right
            else:
                break

        nd_matched = myself

        # ==> Find a replacement node
        if nd_matched.left != nil:
            myself = nd_matched.left
            while True:
                if myself.right == nil:
                    break
                myself = myself.right

            nd_matched.key = myself.key
            nd_matched.value = myself.value

        # ==> Delete node
        # After the previous replacement operation, the target node may have
        # the following situations:
        #
        #   1. Red leaf node                  2. Black leaf node
        #
        #            | [left/right]                    | [left/right]
        #          o---o                             o---o
        #          | R |  (deleting)                 | B |  (deleting)
        #          o---o                             o---o
        #
        #
        #   3. Black node with a right red leaf node
        #
        #            |
        #          +---+
        #          | B |  (deleting)
        #          +---+
        #             \
        #             +---+
        #             | R |
        #             +---+
        #
        # In the second case, it needs to be passed upwards. We will attach the
        # black node to be removed as a ghost to the node passed upwards as an
        # extra black, and digest it through adjustments.
        # Generally, there are three situations, When the sibling node is
        # black, the key is to see whether the nephew node has a red node. If
        # the sibling node is red, it can be rotated to the previous situation.
        #
        #
        #   Legend:
        #       [B]: Black node
        #       [R]: Red node
        #       [B/R]: Black or Red node
        #       [B+*]: Add a layer of black to the original node
        #
        #   1. Sibling node is red
        #                 |                              |
        #               P |                            S |
        #               [ B ]                          [ B ]
        #              /     \ S                    P /     \
        #             /      [R]        ==>        [ R ]     \
        #         M  /    el / \ es             M /     \el   \es
        #     x-> [B+B]     [B]   [B]      x-> [B+B]    [B]   [B]
        #          / \    / \   / \             / \     / \   / \
        #         a   b  c   d e   f           a   b   c   d e   f
        #
        #        a<M<b<P<c<el<d<S<e<es<f      a<M<b<P<c<el<d<S<e<es<f
        #
        #   2. Sibling node is black, there is no red nephew node
        #                 |                            |
        #               P |                          P |
        #              [ B/R ]                 x-> [ B+B/R ]
        #           M /       \ S                  /       \ S
        #      x-> [B+B]       [B]      ==>    M [B]       [R]
        #           / \   el /   \ es            / \   el /   \ es
        #          a   b  [B]     [B]           a   b  [B]     [B]
        #                 / \     / \                  / \     / \
        #                c   d   e   f                c   d   e   f
        #
        #   3. Sibling node is black, but there is at least one red nephew node
        #      exist.
        #                 |                              |
        #               P |                            S |
        #              [ B/R ]                        [ B/R ]
        #           M /       \ S       ==>        P /       \ es
        #      x-> [B+B]      [B]                  [B]       [B]
        #           / \   el /   \ es           M /   \ el   / \
        #          a   b [B/R]    [R]       x-> [B]  [B/R]  e   f
        #                 / \     / \           / \   / \
        #                c   d   e   f         a   b c   d
        #
        #       a<M<b<P<c<el<d<S<e<es<f       a<M<b<P<c<el<d<S<e<es<f
        #
        #      When only another nephew node is red, we could convert to the
        #      above form by simple rotation.
        #                 |                             |
        #               S |                          el |
        #                [B]                           [B]
        #            el /   \           ==>           /   \ S
        #             [R]    \                       a    [R]
        #             / \     \ es                        / \ es
        #            a   b    [B]                        b  [B]
        #                     / \                           / \
        #                    c   d                         c   d
        #
        #          a<el<b<S<c<es<d                  a<el<b<S<c<es<d
        if myself.color == Color.RED:
            if myself.from_direction == Direction.LEFT:
                myself.parent.left = nil
            else:
                myself.parent.right = nil
            return True

        nd_right = myself.right
        if nd_right.color == Color.RED:
            myself.key = nd_right.key
            myself.value = nd_right.value
            myself.right = nil
            return True

        if myself == self.ND_ROOT:
            self.ND_ROOT = self.ND_NULL

        nd_delete = myself
        while True:
            parent = myself.parent
            grandparent = parent.parent
            if myself.from_direction == Direction.LEFT:
                sibling = parent.right
            else:
                sibling = parent.left
            nephew_left = sibling.left
            nephew_right = sibling.right

            if sibling.color == Color.RED:
                sibling.color = Color.BLACK
                parent.color = Color.RED

                sibling.parent = grandparent
                if parent == self.ND_ROOT:
                    self.ND_ROOT = sibling
                else:
                    if parent.from_direction == Direction.LEFT:
                        grandparent.left = sibling
                        sibling.from_direction = Direction.LEFT
                    else:
                        grandparent.right = sibling
                        sibling.from_direction = Direction.RIGHT

                if myself.from_direction == Direction.LEFT:
                    parent.right = nephew_left
                    nephew_left.from_direction = Direction.RIGHT
                    nephew_left.parent = parent

                    sibling.left = parent
                    parent.from_direction = Direction.LEFT
                    parent.parent = sibling
                else:
                    parent.left = nephew_right
                    nephew_right.from_direction = Direction.LEFT
                    nephew_right.parent = parent

                    sibling.right = parent
                    parent.from_direction = Direction.RIGHT
                    parent.parent = sibling

                continue

            if nephew_left.color == nephew_right.color == Color.BLACK:
                sibling.color = Color.RED

                if parent.color == Color.RED:
                    parent.color = Color.BLACK
                    break

                if parent == self.ND_ROOT:
                    break

                myself = parent
                continue

            #         |                |
            #         *                *
            #        / \              / \
            #  x--> B   B            B   B <--x
            #          / \          / \
            #         *   R        R   *
            if (
                    myself.from_direction == Direction.LEFT and \
                    nephew_right.color == Color.RED
               ) or \
               (
                    myself.from_direction == Direction.RIGHT and \
                    nephew_left.color == Color.RED
               ):
                sibling.color = parent.color
                parent.color = Color.BLACK

                sibling.parent = grandparent
                if parent == self.ND_ROOT:
                    self.ND_ROOT = sibling
                else:
                    if parent.from_direction == Direction.LEFT:
                        grandparent.left = sibling
                        sibling.from_direction = Direction.LEFT
                    else:
                        grandparent.right = sibling
                        sibling.from_direction = Direction.RIGHT

                if myself.from_direction == Direction.LEFT:
                    parent.right = nephew_left
                    nephew_left.from_direction = Direction.RIGHT
                    nephew_left.parent = parent

                    sibling.left = parent
                    parent.from_direction = Direction.LEFT
                    parent.parent = sibling

                    nephew_right.color = Color.BLACK
                else:
                    parent.left = nephew_right
                    nephew_right.from_direction = Direction.LEFT
                    nephew_right.parent = parent

                    sibling.right = parent
                    parent.from_direction = Direction.RIGHT
                    parent.parent = sibling

                    nephew_left.color = Color.BLACK

            #         |                |
            #         *                *
            #        / \              / \
            #  x--> B   B            B   B <--x
            #          / \          / \
            #         R   B        B   R

            if myself.from_direction == Direction.LEFT:
                nephew_left.color = parent.color
                parent.color = Color.BLACK

                nephew_left.parent = grandparent
                if parent == self.ND_ROOT:
                    self.ND_ROOT = nephew_left
                else:
                    if parent.from_direction == Direction.LEFT:
                        grandparent.left = nephew_left
                        nephew_left.from_direction = Direction.LEFT
                    else:
                        grandparent.right = nephew_left
                        nephew_left.from_direction = Direction.RIGHT

                parent.right = nephew_left.left
                nephew_left.left.from_direction = Direction.RIGHT
                nephew_left.left.parent = parent

                nephew_left.left = parent
                parent.from_direction = Direction.LEFT
                parent.parent = nephew_left

                sibling.left = nephew_left.right
                nephew_left.right.from_direction = Direction.LEFT
                nephew_left.right.parent = sibling

                nephew_left.right = sibling
                sibling.from_direction = Direction.RIGHT
                sibling.parent = nephew_left

            else:
                nephew_right.color = parent.color
                parent.color = Color.BLACK

                nephew_right.parent = grandparent
                if parent == self.ND_ROOT:
                    self.ND_ROOT = nephew_right
                else:
                    if parent.from_direction == Direction.LEFT:
                        grandparent.left = nephew_right
                        nephew_right.from_direction = Direction.LEFT
                    else:
                        grandparent.right = nephew_right
                        nephew_right.from_direction = Direction.RIGHT

                parent.left = nephew_right.right
                nephew_right.right.from_direction = Direction.LEFT
                nephew_right.right.parent = parent

                nephew_right.right = parent
                parent.from_direction = Direction.RIGHT
                parent.parent = nephew_right

                sibling.right = nephew_right.left
                nephew_right.left.from_direction = Direction.RIGHT
                nephew_right.left.parent = sibling

                nephew_right.left = sibling
                sibling.from_direction = Direction.LEFT
                sibling.parent = nephew_right

            break

        if nd_delete.from_direction == Direction.LEFT:
            nd_delete.parent.left = self.ND_NULL
        else:
            nd_delete.parent.right = self.ND_NULL

        return True

    def pre_order_traversal(self):
        ...

    def in_order_traversal(self):
        ...

    def post_order_traversal(self):
        ...
