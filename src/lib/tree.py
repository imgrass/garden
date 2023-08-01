from .exception import ExceptionBase, register_exception
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Dict, Optional, Type, Union


LOG = getLogger(__name__)


class TreeException(ExceptionBase):

    @register_exception
    def circular_dependency(info, circular_nodes):
        info.tell_me('There is a circular dependency path in the tree: '
                     f'{circular_nodes}')
        info.circular_nodes = circular_nodes


class EigenValue(object):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class _NodeBase(object):

    _name: str
    _parent: Optional['ScalarNode']
    _eigenvalue: EigenValue

    def __init__(self, name: str, eigenvalue: EigenValue,
                 parent: Optional['ScalarNode']=None):
        assert isinstance(eigenvalue, EigenValue)
        assert parent is None or parent.is_container

        self._name = name
        self._eigenvalue = eigenvalue
        if parent is not None:
            self.parent = parent

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, node):
        assert node.is_container
        if hasattr(self, '_parent'):
            self._parent._children.pop(self.unique_id)

        self._parent = node
        node._children[self.unique_id] = self
        self._get_required_nodes()

    @property
    def is_root(self):
        return not hasattr(self, '_parent')

    @property
    def root(self):
        return self._get_required_nodes()[-1]

    @property
    def eigenvalue(self):
        return self._eigenvalue.value

    @property
    def unique_id(self):
        return self._name

    @property
    def is_container(self):
        return isinstance(self, ContainerNode)

    @property
    def is_scalar(self):
        return isinstance(self, ScalarNode)

    @property
    def shown_data(self):
        return f'{self._name}: {self._eigenvalue.value}'

    def _get_required_nodes(self):
        required_nodes = []

        node = self
        while True:
            if node in required_nodes:
                raise TreeException.circular_dependency(
                    [n.unique_id for n in required_nodes])

            required_nodes.append(node)
            if node.is_root:
                break
            node = node.parent

        return required_nodes

    @property
    def path(self):
        required_nodes = self._get_required_nodes()
        required_nodes.reverse()
        return required_nodes

    @property
    def path_level(self):
        return len(self._get_required_nodes())

    def remove(self):
        if self.is_root:
            return

        self._parent._children.pop(self.unique_id)
        del self._parent


class ScalarNode(_NodeBase):
    ...


class ContainerNode(_NodeBase):

    _children: Dict[str, Union['ScalarNode', 'ContainerNode']]

    def __init__(self, name, eigenvalue, parent=None):
        super().__init__(name, eigenvalue, parent=parent)
        self._children = {}

        self._rb_containers = ...
        self._rb_scalars = ...

    def output_tree_mode(self, display_level: int=0) -> str:
        assert display_level >= 0
        result = []

        def _print_tree(node: Union['ScalarNode', 'ContainerNode'],
                        level: int,
                        last: bool=False,
                        header: str=''):
            elbow = '└──'
            tee = '├──'
            pipe = '│  '
            blank = '   '

            if level == 0:
                result.append('%s%s' % (header, node.shown_data))
            else:
                result.append('%s%s%s' % (header, elbow if last else tee,
                                          node.shown_data))
            if display_level != 0 and level >= display_level:
                return
            level += 1

            if node.is_scalar:
                return

            index = 1
            length = len(node._children)
            for key in sorted(node._children):
                child_node = node._children[key]
                if level == 1:
                    _print_tree(child_node, level, last=index==length,
                                header='')
                else:
                    _print_tree(child_node, level, last=index==length,
                                header='%s%s' % (header,
                                                 blank if last else pipe))
                index += 1

        level = 0
        _print_tree(self, level)
        return '\n'.join(result)


class MigrateScheme(ABC):
    r'''
    When migrating from one tree to another, it will be accompanied by the
    adjustment of some nodes, and these adjustment actions will have some
    dependencies. One of the functions of this class is to store these
    adjustment actions and their dependencies.
    In addition, the actual actions corresponding to node adjustments at the
    data structure level are different, which is another function of this class
    '''

    def __init__(self):
        ...

    @abstractmethod
    def create_container_node(self):
        ...

    @abstractmethod
    def move_container_node(self):
        ...

    @abstractmethod
    def copy_container_node(self):
        ...

    @abstractmethod
    def remove_container_node(self):
        ...

    @abstractmethod
    def create_scalar_node(self):
        ...

    @abstractmethod
    def move_scalar_node(self):
        ...

    @abstractmethod
    def copy_scalar_node(self):
        ...

    @abstractmethod
    def remove_scalar_node(self):
        ...

    @abstractmethod
    def generate_container_eigenvalue(self):
        ...

    @abstractmethod
    def generate_scalar_eigenvalue(self):
        ...


class TreeMigration(object):
    r'''
    This module mainly provides a function to figure out the various steps
    required to migrate one tree to another.

    A very common requirement is that users can not directly operate a
    directory, but need to go through a proxy, such as HTTP servers. At this
    time, the content of the files and the structure of the file tree may be
    changed on the client side. If the entire files are replaced directly, the
    performance waste will be serious. Then we hope to find the operation steps
    with the least impact as much as possible.

    For example:

             (x_x) old tree                          (^_<) new tree
                                 ======---->
                   root            migrate               root
               -------------                         -------------
                /  \     \                            /  \     \
               /    \     \                          /    \     \
            node1  node2  node3                   node5  node2  node4
             / \     |     |                        |      |     | \
            /   \    |     |                        |      |     |  \
           f1   f2   f3    f4                     node6    f3'  f4  f5
                                                   / \
                                                  /   \
                                                 f1   f2

        1. Adjust the branches, create new directories:

            * mkdir -p root/node4 root/node5

            # Notice that the sub-directory (node1) in old tree has the same
            content of the sub-directory (node5) in new tree, so we handle it
            as the same as the file node.

        2. Move or cp the file nodes and sub-directory nodes with the same
           content:

            * mv root/node1     root/node5/node6
            * mv root/node3/f4  root/node4/f4

        3. Replace the changed files:

            * cp f3' root/node2/f3'

        4. Add new files:

            * cp f5 root/node4/f5

        5. Remove un-needed directory and files:

            * rm -rf node3/
    '''

    def __init__(self, tree_from: ContainerNode, tree_to: ContainerNode,
                 migrate_scheme_cls: Type[MigrateScheme]):
        assert isinstance(tree_from, ContainerNode)
        assert isinstance(tree_to, ContainerNode)
        assert issubclass(migrate_scheme_cls, MigrateScheme)

        if not tree_from.is_root:
            raise TypeError('The tree migrated from is not the root node')
        if not tree_to.is_root:
            raise TypeError('The tree migrated to is not the root node')

        self._tree_from = tree_from
        self._tree_to = tree_to
        self._scheme = migrate_scheme_cls()

    def calculate(self):
        ...

    def execute(self):
        ...


__all__ = ('TreeMigration', 'ContainerNode', 'ScalarNode')
