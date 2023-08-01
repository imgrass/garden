import __data__.fake_tree as fake_tree
from imgrass_horizon.lib.tree import (
    ContainerNode, EigenValue, ScalarNode, TreeException, TreeMigration
)
from logging import getLogger
from pytest import raises as pytest_raise
from typing import List


LOG = getLogger(__name__)


def generate_tree(root_name: str, tree_desc: List) -> ContainerNode:

    containers = {}

    for node_desc in tree_desc:
        if 'container_name' not in node_desc:
            continue

        if node_desc['container_name'] in containers:
            raise Exception(
                f'Duplicated container node({node_desc["container_name"]}) '
                'was found, please check the <container_name> definition.')

        containers[node_desc['container_name']] = ContainerNode(
            node_desc['name'], EigenValue(node_desc['eigenvalue']))

    for node_desc in tree_desc:
        if 'container_name' in node_desc:
            if 'parent' in node_desc:
                containers[node_desc['container_name']].parent = \
                        containers[node_desc['parent']]
        else:
            ScalarNode(node_desc['name'], EigenValue(node_desc['eigenvalue']),
                       parent=containers[node_desc['parent']])

    root_node = containers[root_name]
    if not root_node.is_root:
        raise Exception('The container node described with '
                        f'<<container_name={root_name}>> is not the root node')

    return root_node


class TestTree(object):

    def test_display_with_tree_mode(self):
        nd_root = ContainerNode('/', EigenValue('D0'))
        nd_file1 = ScalarNode('file1', EigenValue('F0-1'), parent=nd_root)
        ScalarNode('file2', EigenValue('F0-2'), parent=nd_root)

        nd_dir1 = ContainerNode('dir1', EigenValue('D1-1'), parent=nd_root)
        ScalarNode('file1', EigenValue('F1-1-1')).parent = nd_dir1
        ScalarNode('file2', EigenValue('F1-1-2')).parent = nd_dir1

        nd_dir2 = ContainerNode('dir2', EigenValue('D1-2'), parent=nd_dir1)
        ScalarNode('file1', EigenValue('F1-2-1'), parent=nd_dir2)
        nd_file2 = ScalarNode('file2', EigenValue('F1-2-2'), parent=nd_dir2)

        assert nd_root.output_tree_mode() == fake_tree.NORMAL_TREE_DISPLAY
        assert nd_root.is_root == True
        assert nd_dir1.is_root == False
        assert nd_dir2.is_root == False

        assert [n.unique_id for n in nd_file1.path] == ['/', 'file1']
        assert [n.unique_id for n in nd_file2.path] == \
               ['/', 'dir1', 'dir2', 'file2']

    def test_circular_dependency(self):
        nd_a = ContainerNode('a', EigenValue('0'))
        nd_b = ContainerNode('b', EigenValue('1'))

        nd_a.parent = nd_b

        with pytest_raise(TreeException) as exc_info:
            nd_b.parent = nd_a

        assert exc_info.value.info.circular_nodes == ['b', 'a']


class TestTreeMigration(object):

    def test_migrate_tree(self):
        tree_from = generate_tree('root', fake_tree.TREE_FROM)
        tree_to = generate_tree('root', fake_tree.TREE_TO)

        assert tree_from.output_tree_mode() == fake_tree.TREE_FROM_DISPLAY
        assert tree_to.output_tree_mode() == fake_tree.TREE_TO_DISPLAY
