'''
.Insert 1000
.Expect as root node

.Insert 500
.Expect:
    .Search left branch of 1000
    .As leaf node

.Insert 1500
.Expect:
    .Search right branch of 1000
    .As leaf node

.Insert 250, 1750, 1250, 125, 65, 2000, 95, 2500, 350, 750, 400, 380

.Validate:
    .(Is valid red-black tree)

.Insert 390
.Expect:
    .Search left branch of 1000
    .Search right branch of 250
    .Search left branch of 500
    .Search right branch of 380
    .Search left branch of 400
    .As leaf node
    .Fixup red-uncle RL
    .Fixup black-uncle RL
'''


INSERTION_STEPS = '''
- + 1000:
  - as root

- + 500:
  - s 1000 <-
  - as leaf

- + 1500:
  - s 1000 ->
  - as leaf

- + 250:
  - s 1000 <-
  - s 500 <-
  - as leaf
  - f red-uncle LL
  - f red-root

- + 1750:
  - s 1000 ->
  - s 1500 ->
  - as leaf

- + 1250:
  - s 1000 ->
  - s 1500 <-
  - as leaf

- + 125:
  - s 1000 <-
  - s 500 <-
  - s 250 <-
  - as leaf
  - f black-uncle LL

- + 65:
  - s 1000 <-
  - s 250 <-
  - s 125 <-
  - as leaf
  - f red-uncle LL

- + 2000:
  - s 1000 ->
  - s 1500 ->
  - s 1750 ->
  - as leaf
  - f red-uncle RR

- + 95:
  - s 1000 <-
  - s 250 <-
  - s 125 <-
  - s 65 ->
  - as leaf
  - f black-uncle LR

- + 2500:
  - s 1000 ->
  - s 1500 ->
  - s 1750 ->
  - s 2000 ->
  - as leaf
  - f black-uncle RR

- + 350:
  - s 1000 <-
  - s 250 ->
  - s 500 <-
  - as leaf

- + 750:
  - s 1000 <-
  - s 250 ->
  - s 500 ->
  - as leaf

- + 400:
  - s 1000 <-
  - s 250 ->
  - s 500 <-
  - s 350 ->
  - as leaf
  - f red-uncle LR
  - f red-uncle LR
  - f red-root

- + 380:
  - s 1000 <-
  - s 250 ->
  - s 500 <-
  - s 350 ->
  - s 400 <-
  - as leaf
  - f black-uncle RL

- + 390:
  - s 1000 <-
  - s 250 ->
  - s 500 <-
  - s 380 ->
  - s 400 <-
  - as leaf
  - f red-uncle RL
  - f black-uncle RL
'''

# The Red-Black tree structure of INSERTION_STEPS is shown in the figure below
#
#                                     [1000]
#                                      /  \
#                         o-----------o    o-----------o
#                        /                              \
#                    [380]                             [1500]
#                    /   \                              /  \
#             o-----o     o-----o                      /    \
#            /                   \                    o      o
#         (250)                 (500)                 |      |
#         /   \                 /   \                 o      o
#        /     \               /     \               /        \
#      [95]    [350]        [400]   [750]        [1250]     [2000]
#     /    \                /                               /     \
#    /      \              /                               /       \
#  (65)   (125)          (390)                          (1750)    (2500)
#
#
# Legend:
#   - [*]       Black node
#   - (*)       Red node


INSERT_DUPLICATE_KEY_STEPS = INSERTION_STEPS + '''

- + 1250:
  - s 1000 ->
  - s 1500 <-
  - s 1250 <-
  - as leaf
'''


SEARCH_400_STEPS = INSERTION_STEPS + '''
- / 400:
  - s 1000 <-
  - s 380 ->
  - s 500 <-
  - match 400
'''


SEARCH_450_STEPS = INSERTION_STEPS + '''
- / 450:
  - s 1000 <-
  - s 380 ->
  - s 500 <-
  - s 400 ->
  - unmatch
'''


DELETION_STEPS = INSERTION_STEPS + '''

- - 1000:
  - match 1000
  - s 380 ->
  - s 500 ->
  - s 750 ->
  - replace 1000 with 750
  - remove 750
  - fd black-brother LL
'''
