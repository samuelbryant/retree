import unittest, re

from retree import ReTree


class BaseTestCase(unittest.TestCase):

    verbose = False

    def get_tree(self, pattern, text):
        if self.verbose:
            print('Running test:')
            print('\tpattern = %s' % pattern)
            print('\ttext    = %s' % text)
        pattern = re.compile(pattern)
        match = pattern.match(text)
        return ReTree.from_match(match)

    def assert_basic(self, node, label, exp_root=(), exp_parent=(), exp_has_children=(), exp_is_root=(), exp_match=(), exp_depth=(), exp_text=()):
        if exp_root is not ():
            self.assertEqual(
                node.root, exp_root, '%s root should be %s' % (label, str(exp_root)))
        if exp_parent is not ():
            self.assertEqual(
                node.root, exp_root, '%s parent should be %s' % (label, str(exp_parent)))
        if exp_match is not ():
            self.assertEqual(
                node.match, exp_match, '%s match should be %s' % (label, str(exp_match)))
        if exp_depth is not ():
            self.assertEqual(
                node.get_depth(), exp_depth, '%s depth should be %s' % (label, str(exp_depth)))
        if exp_text is not ():
            self.assertEqual(
                node.text, exp_text, '%s text should be %s' % (label, str(exp_text)))
        if exp_has_children is True:
            self.assertTrue(
                node.has_children(), '%s should have children' % str(label))
        elif exp_has_children is False:
            self.assertFalse(
                node.has_children(), '%s should not have children' % str(label))
        if exp_is_root is True:
            self.assertTrue(
                node.is_root(), '%s should be root' % str(label))
        elif exp_is_root is False:
            self.assertFalse(
                node.is_root(), '%s should not be root' % str(label))

class TestGetDepthBasic(BaseTestCase):
    verbose = False

    def test_with_no_groups(self):
        root = self.get_tree('cat', 'cat')
        self.assertEqual(root.get_depth(), 1)

    def test_with_full_nested_group(self):
        root = self.get_tree('(cat)', 'cat')
        self.assertEqual(root.get_depth(), 2)
        root = self.get_tree('((cat))', 'cat')
        self.assertEqual(root.get_depth(), 3)
        root = self.get_tree('(((cat)))', 'cat')
        self.assertEqual(root.get_depth(), 4)

    def test_with_partial_nested_group(self):
        root = self.get_tree('dog(cat)dog', 'dogcatdog')
        self.assertEqual(root.get_depth(), 2)
        root = self.get_tree('dog((cat))dog', 'dogcatdog')
        self.assertEqual(root.get_depth(), 3)
        root = self.get_tree('dog(((cat)))dog', 'dogcatdog')
        self.assertEqual(root.get_depth(), 4)

    def test_with_complex(self):
        regex = '123((cat)(dog)(cat(dog)))(hamburger)456'
        text = '123catdogcatdoghamburger456'
        root = self.get_tree(regex, text)
        self.assertEqual(root.get_depth(), 4, 'Expected match to have depth of 4')


class TestBasicFunctions(BaseTestCase):
    verbose = False

    def test_from_match_with_bare_match(self):
        root = self.get_tree('cat', 'cat')
        self.assertTrue(root.is_root())
        self.assertEqual(root.text, 'cat')

    def test_from_match_without_matching(self):
        root = self.get_tree('catdog', 'cat')
        self.assertEqual(root, None)

    def test_is_root(self):
        # Tree with only root
        root = self.get_tree('cat', 'cat')
        self.assertTrue(root.is_root(), 'Root should be root')

        # Tree with one child
        root = self.get_tree('(cat)', 'cat')
        self.assertTrue(root.is_root(), 'Root should be root')
        self.assertFalse(root.children[0].is_root(), 'Child should not be root')

        # Tree with more complex structure
        root = self.get_tree('((cat(mouse))dog(fish))', 'catmousedogfish')
        self.assertTrue(root.is_root(), 'Root should be root')
        notRoot = lambda node: self.assertFalse(node.is_root(),'Child should not be root')
        for child in root.children:
            child.do_for_all(notRoot)

    def test_relations_when_only_root(self):
        root = self.get_tree('cat', 'cat')
        self.assert_basic(
            root, 'Root', exp_has_children=False, exp_root=root, exp_is_root=True, exp_parent=None,
            exp_depth=1, exp_match=root.match)

    def test_relations_with_simple_depth_2(self):
        root = self.get_tree('(cat)', 'cat')
        self.assert_basic(
            root, 'Root', exp_has_children=True, exp_root=root, exp_is_root=True, exp_parent=None,
            exp_depth=2, exp_match=root.match)
        node = root.children[0]
        self.assert_basic(
            node, 'Child', exp_has_children=False, exp_root=root, exp_is_root=False, exp_parent=root,
            exp_depth=1, exp_match=root.match)

    def test_relations_with_simple_depth_3(self):
        root = self.get_tree('((cat))', 'cat')
        node = root
        child = root.children[0]
        leaf = child.children[0]
        self.assert_basic(
            root, 'Root', exp_has_children=True, exp_root=root, exp_is_root=True, exp_parent=None,
            exp_depth=3, exp_match=root.match)
        self.assert_basic(
            child, 'Child', exp_has_children=True, exp_root=root, exp_is_root=False, exp_parent=root,
            exp_depth=2, exp_match=root.match)
        self.assert_basic(
            leaf, 'Leaf child', exp_has_children=False, exp_root=root, exp_is_root=False, exp_parent=child,
            exp_depth=1, exp_match=root.match)

    def test_when_subgroup_is_group(self):
        pattern = re.compile('(dog)((cat))')
        rt = ReTree.from_match(pattern.match('dogcat'))
        c1 = rt.children[0]
        c2 = rt.children[1]
        cc = c2.children[0]
        self.assert_basic(c1, 'Child1' , exp_text='dog', exp_has_children=False)
        self.assert_basic(c2, 'Child2' , exp_text='cat', exp_has_children=True)
        self.assert_basic(cc, 'Child21', exp_text='cat', exp_has_children=False)

class TestDoForAll(BaseTestCase):

    def check_list_match(self, list1, list2):
        if type(list1) == 'list' and type(list2) == 'list':
            if len(list1) != len(list2):
                return False
            for i in range(len(list1)):
                if not self.check_list_match(list1[i], list2[i]):
                    return False
            return True
        else:
            return list1 == list2

    def assert_list_match(self, act, exp):
        equal = self.check_list_match(act, exp)
        self.assertTrue(equal, 'Expected lists to match:\n\texp=%s\n\tact=%s' % (str(exp), str(act)))

    def test_bare_root(self):
        entries = []
        func = lambda node: entries.append((node.index, node.text))
        root = self.get_tree('cat', 'cat')
        exp_entries = [(0, 'cat')]
        root.do_for_all(func)
        self.assert_list_match(entries, exp_entries)

    def test_simple_nested_groups_n2(self):
        entries = []
        func = lambda node: entries.append((node.index, node.text))
        root = self.get_tree('(cat)', 'cat')
        exp_entries = [(0, 'cat'), (1, 'cat')]
        root.do_for_all(func)
        self.assert_list_match(entries, exp_entries)

    def test_simple_nested_groups_n2(self):
        entries = []
        func = lambda node: entries.append((node.index, node.text))
        root = self.get_tree('((cat))', 'cat')
        exp_entries = [(0, 'cat'), (1, 'cat'), (2, 'cat')]
        root.do_for_all(func)
        self.assert_list_match(entries, exp_entries)

    def test_complex(self):
        entries = []
        func = lambda node: entries.append((node.index, node.text))

        regex = '((([0-9])([0-9])([0-9])) (cat) (([0-9])([0-9])))'
        text  = '123 cat 45'
        exp_entries = [(0, '123 cat 45'), (1, '123 cat 45'), (2, '123'), (3, '1'), (4, '2'), (5, '3'), (6, 'cat'), (7, '45'), (8, '4'), (9, '5')]
        root = self.get_tree(regex, text)
        root.do_for_all(func)
        self.assert_list_match(entries, exp_entries)

class TestComplexLog(BaseTestCase):
    pattern: re.Pattern
    REGEX = ' '.join([
        r'(([0-9]{4})-([0-9]{2})-([0-9]{2}))',            # Date
        r'(([0-9]{2}):([0-9]{2}):([0-9]{2}))\.[0-9]+',    # Timestamp
        r'([^,]+)',                                       # Some message
    ])

    def setUp(self):
        self.pattern = re.compile(self.REGEX)

    def build_test_string(self, year=2024, month=12, date=11, hour=10, minute=9, second=8.7, message='Test message'):
        data = {}
        data['year'] = year
        data['month'] = month
        data['date'] = date
        data['hour'] = hour
        data['minute'] = minute
        data['second'] = second
        data['message'] = message
        text = '%04d-%02d-%02d %02d:%02d:%09f %s' % (year, month, date, hour, minute, second, message)
        return text, data

    def test_example_builds_correctly(self):
        text, test_data = self.build_test_string();
        self.assertEqual(text, '2024-12-11 10:09:08.700000 Test message')
        text, test_data = self.build_test_string(
            year=2023, month=9, date=8, hour=7, minute=6, second=5.3, message='Other test message');
        self.assertEqual(text, '2023-09-08 07:06:05.300000 Other test message')

    def test_builds_successfully(self):
        text = '2024-12-04 00:05:00.030030 This is a message'
        root = self.get_tree(self.REGEX, text)
        self.assertTrue(root.is_root())

    def test_builds_with_correct_text(self):
        text, _ = self.build_test_string();
        root = self.get_tree(self.REGEX, text)
        child0 = root.children[0]
        child1 = root.children[1]
        child2 = root.children[2]
        self.assert_basic(root, 'Root', exp_text = text)
        self.assert_basic(child0, 'Child0', exp_text = '2024-12-11')
        self.assert_basic(child0.children[0], 'Child0.0', exp_text='2024')
        self.assert_basic(child0.children[1], 'Child0.1', exp_text='12')
        self.assert_basic(child0.children[2], 'Child0.2', exp_text='11')
        self.assert_basic(child1, 'Child1', exp_text = '10:09:08')
        self.assert_basic(child1.children[0], 'Child1.0', exp_text='10')
        self.assert_basic(child1.children[1], 'Child1.1', exp_text='09')
        self.assert_basic(child1.children[2], 'Child1.2', exp_text='08')
        self.assert_basic(child2, 'Child2', exp_text = 'Test message')

    def test_builds_with_correct_properties(self):
        text, _ = self.build_test_string();
        root = self.get_tree(self.REGEX, text)
        child0 = root.children[0]
        child1 = root.children[1]
        child2 = root.children[2]
        self.assert_basic(root, 'Root', exp_text = text,
            exp_depth = 3,
            exp_root = root,
            exp_parent = None,
            exp_has_children = True,
            exp_is_root = True,
            exp_match = root.match)

        # Test intermediary child
        self.assert_basic(child0, 'Child0', exp_text = '2024-12-11',
            exp_depth = 2,
            exp_root = root,
            exp_parent = root,
            exp_has_children = True,
            exp_is_root = False,
            exp_match = root.match)

        # Test leaf child
        self.assert_basic(child1.children[2], 'Child1.2', exp_text='08',
            exp_depth = 1,
            exp_root = root,
            exp_parent = child1,
            exp_has_children = False,
            exp_is_root = False,
            exp_match = root.match)

    def test_builds_with_correct_number_of_children(self):
        text, test_data = self.build_test_string();
        rt = ReTree.from_match(self.pattern.match(text))
        exp_structure = [[[], [], []], [[], [], []], []]

        exp_struct = exp_structure
        act_node = rt
        def sub_test(exp_struct, node):
            assertEqual(len(node.children), len(exp_struct), 'Node has wrong # of children')
            for i, c in enumerate(node.children):
                sub_test(exp_struct[i], c)

# Running the tests
if __name__ == '__main__':
    unittest.main()




