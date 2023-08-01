from textwrap import dedent


NORMAL_TREE_DISPLAY = dedent('''
    /: D0
    ├──dir1: D1-1
    │  ├──dir2: D1-2
    │  │  ├──file1: F1-2-1
    │  │  └──file2: F1-2-2
    │  ├──file1: F1-1-1
    │  └──file2: F1-1-2
    ├──file1: F0-1
    └──file2: F0-2
''').strip('\n')


TREE_FROM_DISPLAY = dedent('''
    root: 00000000
    ├──node1: ffff0001
    │  ├──f1: cccc0001
    │  └──f2: cccc0010
    ├──node2: ffff0010
    │  └──f3: cccc0100
    └──node3: ffff0100
       └──f4: cccc1000
''').strip('\n')
TREE_FROM = [
    {
        'name': 'root',
        'eigenvalue': '00000000',
        'container_name': 'root'
    },
    {
        'name': 'node1',
        'eigenvalue': 'ffff0001',
        'container_name': 'node1',
        'parent': 'root'
    },
    {
        'name': 'f1',
        'eigenvalue': 'cccc0001',
        'parent': 'node1'
    },
    {
        'name': 'f2',
        'eigenvalue': 'cccc0010',
        'parent': 'node1'
    },
    {
        'name': 'node2',
        'eigenvalue': 'ffff0010',
        'container_name': 'node2',
        'parent': 'root'
    },
    {
        'name': 'f3',
        'eigenvalue': 'cccc0100',
        'parent': 'node2'
    },
    {
        'name': 'node3',
        'eigenvalue': 'ffff0100',
        'container_name': 'node3',
        'parent': 'root'
    },
    {
        'name': 'f4',
        'eigenvalue': 'cccc1000',
        'parent': 'node3'
    }
]


TREE_TO_DISPLAY = dedent('''
    root: ffffffff
    ├──node2: eeee0100
    │  └──f3: cccc0200
    ├──node4: eeee0010
    │  ├──f4: cccc1000
    │  └──f5: dddd0001
    └──node5: eeee0001
       └──node6: ffff0001
          ├──f1: cccc0001
          └──f2: cccc0010
''').strip('\n')
TREE_TO = [
    {
        'name': 'root',
        'eigenvalue': 'ffffffff',
        'container_name': 'root'
    },
    {
        'name': 'node5',
        'eigenvalue': 'eeee0001',
        'container_name': 'node5',
        'parent': 'root'
    },
    {
        'name': 'node6',
        'eigenvalue': 'ffff0001',
        'container_name': 'node6',
        'parent': 'node5'
    },
    {
        'name': 'f1',
        'eigenvalue': 'cccc0001',
        'parent': 'node6'
    },
    {
        'name': 'f2',
        'eigenvalue': 'cccc0010',
        'parent': 'node6'
    },
    {
        'name': 'node2',
        'eigenvalue': 'eeee0100',
        'container_name': 'node2',
        'parent': 'root'
    },
    {
        'name': 'f3',
        'eigenvalue': 'cccc0200',
        'parent': 'node2'
    },
    {
        'name': 'node4',
        'eigenvalue': 'eeee0010',
        'container_name': 'node4',
        'parent': 'root'
    },
    {
        'name': 'f4',
        'eigenvalue': 'cccc1000',
        'parent': 'node4'
    },
    {
        'name': 'f5',
        'eigenvalue': 'dddd0001',
        'parent': 'node4'
    }
]
